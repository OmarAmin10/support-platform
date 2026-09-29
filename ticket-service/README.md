# Ticket Service

A Django REST Framework API for creating and managing support tickets. The service uses JWT authentication, applies role-based ticket visibility, validates agent assignments through an external Auth service, and publishes ticket events to Kafka.

> This repository is an active development project. See [known implementation notes](docs/API.md#implementation-notes) before relying on every documented workflow.

## Features

- Create tickets as a customer.
- List tickets according to the authenticated user's role.
- Retrieve, update, and delete tickets with ownership/role checks.
- Allow administrators to assign a ticket to a verified agent.
- Publish ticket-created and ticket-assigned events to Kafka.
- Browse the OpenAPI schema and Swagger UI.

## Requirements

- Python and pip.
- PostgreSQL. In the provided Compose setup, the host ports are `5434` for Auth DB and `5435` for Ticket DB; containers connect to the databases on port `5432` using service names.
- A JWT issuer that signs tokens with the same `JWT_SIGNING_KEY` and includes a numeric user ID and a `role` claim.
- The Auth service, for agent verification during assignment.
- Kafka available at `localhost:9092`.

There is currently no dependency lockfile or requirements file in the repository. Install the packages used by the codebase in your virtual environment: Django, Django REST Framework, djangorestframework-simplejwt, drf-spectacular, psycopg (or psycopg-binary), python-dotenv, requests, and confluent-kafka.

## Local Setup

Run these commands from the repository root in PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install Django djangorestframework djangorestframework-simplejwt drf-spectacular "psycopg[binary]" python-dotenv requests confluent-kafka
```

Create a local `.env` file in the repository root. Keep real credentials out of source control:

```dotenv
DB_PASSWORD=replace-with-your-postgres-password
JWT_SIGNING_KEY=replace-with-the-shared-jwt-signing-key
AUTH_SERVICE_URL=http://localhost:8001
```

`AUTH_SERVICE_URL` is the base URL of the Auth service. Agent assignment requests its profile endpoint at `/api/profile/<user_id>`.

Create a PostgreSQL database named `ticket_db` and ensure the configured database user can access it on port `5433`. Then run migrations and start Django:

```powershell
python manage.py migrate
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/` by default. Kafka must be running before code paths that publish ticket events are exercised. The producer reads `KAFKA_BOOTSTRAP_SERVERS`; use `localhost:9092` when running the service on the host, or `kafka:9092` from the Compose network. Events use topic `ticket-events`.

## Docker Compose

From the `support-platform` directory, create a root `.env` containing `JWT_SIGNING_KEY` (the same signing key used by the Auth service), then start the stack:

```powershell
docker compose up --build
```

Compose exposes the Ticket API on port `8000`, the Auth service on `8001`, Kafka on `9092`, and the databases on host ports `5434` and `5435`. The JWT signing key is deliberately required from the environment rather than stored in the Compose file.

## API Documentation

- Interactive Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`
- Endpoint and role reference: [docs/API.md](docs/API.md)

API endpoints require a valid JWT unless otherwise noted. Send it as:

```http
Authorization: Bearer <access-token>
```

The token must be compatible with this service's configured signing key and contain the claims used by the API: user ID and `role` (`CUSTOMER`, `AGENT`, or `ADMIN`). Token issuance is not implemented in this service.

## Event Messages

Events are JSON messages sent to Kafka topic `ticket-events`:

- `TICKET_CREATED`: includes `ticket_id`, `customer_id`, and `status`.
- `TICKET_ASSIGNED`: includes `ticket_id`, `agent_id`, and `customer_id`.

## Development Checks

```powershell
python manage.py check
python manage.py test
```

The test module currently has no test cases, so add API and service tests before treating the checks as behavioral coverage.

## Configuration and Deployment

The checked-in Django settings are development-oriented (`DEBUG = True`) and contain a hard-coded Django secret key. Do not deploy with those defaults. Before deployment, move secrets to environment variables, configure `DEBUG = False` and `ALLOWED_HOSTS`, use production-grade database/Kafka/Auth service settings, and review Django's deployment checklist.
