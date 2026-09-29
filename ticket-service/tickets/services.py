from .models import Ticket
from django.shortcuts import get_object_or_404
from .clients import AuthClient
from .kafka_producer import publish_event


class TicketService:

    VALID_STATUS_TRANSITIONS ={
      "OPEN":["IN_PROGRESS"],
      "IN_PROGRESS":["RESOLVED"],
      "RESOLVED":["CLOSED"],
      "CLOSED":[]
}

    @staticmethod
    def get_all_tickets(customer_id):
        return Ticket.objects.filter(customer_id=customer_id)


    @staticmethod
    def create_ticket(validated_data,customer_id):

        ticket = Ticket.objects.create(**validated_data,
                                       customer_id = customer_id)

        publish_event("ticket-events",
        {
              "event_type":"TICKET_CREATED",
              "ticket_id":ticket.id,
              "customer_id":ticket.customer_id,
              "status":ticket.status
        })
        
        return ticket

    @staticmethod
    def get_ticket(ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        return ticket

    @staticmethod
    def update_ticket(ticket,validated_data): 
             old_status = ticket.status
             for field , value in validated_data.items():
                  setattr(ticket,field,value)

             ticket.save()
             if old_status != ticket.status:
                   publish_event("ticket-events",
                           {
                                 "event_type":"TICKET_STATUS_CHANGED",
                                 "ticket_id":ticket.id,
                                 "old_status":old_status,
                                 "status":ticket.status,
                                 "customer_id":ticket.customer_id
                           })
             return ticket     

    @staticmethod
    def delete_ticket(ticket):
          ticket.delete()



    @staticmethod
    def get_tickets_by_agent(agent_id):
         tickets = Ticket.objects.filter(assigned_agent_id=agent_id)
         return tickets

    @staticmethod
    def get_tickets_by_customer(customer_id):
             tickets = Ticket.objects.filter(customer_id=customer_id)
             return tickets  

    @staticmethod
    def get_all_tickets():
          return Ticket.objects.all()


    @staticmethod
    def assign_ticket_to_agent(ticket,agent_id,access_token):
          response = AuthClient.get_user(agent_id,access_token)
          print(response)
          if response is None:
                return None
          if response.status_code != 200:
                return None

          user_data = response.json()
          print(user_data,"user")
          if user_data.get("role") != "ADMIN":
                return None

          ticket.assigned_agent_id=agent_id
          ticket.save()

          publish_event("ticket-events",
           {
           "event_type":"TICKET_ASSIGNED",
            "ticket_id":ticket.id,
            "agent_id":ticket.assigned_agent_id,
            "customer_id":ticket.customer_id,
                  })

          return ticket

    @staticmethod
    def is_valid_status_transition(current_status,new_status):
          allowed_statuses = TicketService.VALID_STATUS_TRANSITIONS.get(
                current_status,
                []
          )

          return new_status in allowed_statuses      
                
     
    

