# Ticket Service API

Base URL for local development: `http://127.0.0.1:8000/api`

All listed endpoints require JWT authentication. Include an access token in the `Authorization` header:

```http
Authorization: Bearer <access-token>
Content-Type: application/json
```

The token is validated using the shared signing key configured in the service. Views read the user's numeric ID and `role` claim. Supported role values are `CUSTOMER`, `AGENT`, and `ADMIN`.

## Ticket Data

The ticket serializer exposes these fields:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Database-generated ticket ID. |
| `title` | string | Maximum length 20 characters. |
| `description` | string | Maximum length 20 characters. |
| `customer_id` | integer | Assigned from the authenticated user when creating; marked read-only in the serializer. |
| `assigned_agent_id` | integer or null | Empty until assigned. |
| `status` | string | One of `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`; defaults to `OPEN`. |
| `priority` | string | One of `LOW`, `MEDIUM`, `HIGH`, `URGENT`; defaults to `LOW`. |
| `created_at` | datetime | Set when created. |
| `updated_at` | datetime | Updated when saved. |

## Endpoints

### List tickets

`GET /api/tickets/`

- `CUSTOMER`: returns tickets whose `customer_id` matches the authenticated user.
- `AGENT`: returns tickets assigned to the authenticated user.
- `ADMIN`: returns all tickets.
- Other role values are rejected with `403 Forbidden`.

Successful response: a JSON array of ticket objects. An empty array means no tickets matched.

### Create a ticket

`POST /api/tickets/`

Customer request body:

```json
{
  "title": "Cannot sign in",
  "description": "Password reset link fails",
  "priority": "HIGH"
}
```

The service sets `customer_id` using the authenticated user's ID. On success, it returns the created ticket with `201 Created` and publishes a `TICKET_CREATED` event to Kafka.

The current view explicitly blocks `ADMIN` and `AGENT` roles. It does not explicitly reject unknown role values in this method, so clients should only use supported roles.

### Retrieve a ticket

`GET /api/ticket/{ticket_id}/`

- Customers can retrieve their own tickets.
- Agents can retrieve tickets assigned to them.
- Administrators can retrieve any ticket.
- An unsupported role or an ownership mismatch returns `403 Forbidden`.
- An unknown ticket ID raises a `404 Not Found` response through the service lookup.

The current view returns `201 Created` for a successful GET; this should be corrected to `200 OK`.

### Update a ticket

`PATCH /api/ticket/{ticket_id}/`

The request is a partial ticket object. The view intends to apply role-specific field restrictions and validates status changes against this transition sequence:

```text
OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED
```

Current intended field permissions:

- Customer: `title`, `description`.
- Assigned agent: `status`.
- Administrator: `title`, `description`, `status`, `priority`.

The current implementation has errors in these allowlists: it spells customer `description` as `decription`, and combines admin `status` and `priority` into a single string (`status,priority`). As a result, valid updates to those fields are rejected. Correct these allowlists before relying on PATCH.

The view also does not reject unsupported roles before selecting an allowlist, so a token with an unknown role can trigger a server error on this endpoint. Reject unsupported roles explicitly.

### Delete a ticket

`DELETE /api/ticket/{ticket_id}/`

The view allows the ticket's customer or an administrator to delete; agents are rejected. On success it currently returns `202 Accepted` with an empty body. The ticket lookup raises 404 for unknown IDs before the view's `None` check.

### Assign a ticket to an agent

`PATCH /api/tickets/{ticket_id}/assign/`

Administrator-only. Request body:

```json
{
  "agent_id": 42
}
```

The ticket service calls the Auth service endpoint:

```text
{AUTH_SERVICE_URL}/api/profile/{agent_id}
```

It forwards the caller's Bearer token and expects HTTP `200 OK` with a JSON body containing `{"role": "AGENT"}`. A successful assignment updates `assigned_agent_id`, returns the ticket, and publishes a `TICKET_ASSIGNED` event. An unavailable Auth service is intended to return `503 Service Unavailable`.

The current view expects the `Authorization` header to contain a two-part Bearer token. The current generic failure response says `No Ticket Found` when agent verification fails; that response can mean the Auth service rejected the agent or returned a non-agent role, not that the ticket ID was missing. A missing ticket is returned as 404 by the service lookup.

### Inspect authenticated token identity

`GET /api/test-auth/`

Returns the authenticated user ID and the role claim. This is a development/debug endpoint and should be reviewed or removed before production.

## HTTP Status Summary

| Status | Meaning |
| --- | --- |
| `200 OK` | Successful list, patch, assignment, or standard retrieval (the current detail GET mistakenly returns 201). |
| `201 Created` | Ticket created. |
| `202 Accepted` | Ticket deleted by the current implementation. |
| `400 Bad Request` | Invalid input, invalid status transition, or unsuccessful agent verification (current assignment error wording is inaccurate). |
| `401 Unauthorized` | Missing or invalid authentication credentials. |
| `403 Forbidden` | Role or ticket ownership does not permit the operation. |
| `404 Not Found` | Ticket ID does not exist. |
| `503 Service Unavailable` | Auth service is unavailable during agent assignment. |

## Event Contract

Events are JSON-encoded and published to Kafka topic `ticket-events`.

Ticket created:

```json
{
  "event_type": "TICKET_CREATED",
  "ticket_id": 1,
  "customer_id": 7,
  "status": "OPEN"
}
```

Ticket assigned:

```json
{
  "event_type": "TICKET_ASSIGNED",
  "ticket_id": 1,
  "agent_id": 42,
  "customer_id": 7
}
```

The producer reads `KAFKA_BOOTSTRAP_SERVERS`. In Docker Compose it is set to `kafka:9092`; when running the service directly on the host, use `localhost:9092`. The Compose broker publishes events through topic `ticket-events`.

## OpenAPI Endpoints

- Swagger UI: `/api/docs/`
- OpenAPI schema: `/api/schema/`

## Implementation Notes

This document describes the routes and current code behavior, while calling out known mismatches. In particular, fix the PATCH allowlist typos, return `200 OK` for detail GET, remove debug `print()` calls, and add endpoint tests before treating the API contract as stable. The `tickets/tests.py` module currently contains no behavioral tests.
