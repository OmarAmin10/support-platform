from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from .serializers import TicketSerializer
from .models import Ticket
from .services import TicketService
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin
from .clients import AuthServiceUnavailable

class TicketsView(generics.ListCreateAPIView):
    # queryset = Ticket.objects.all()
    # serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get(self,request):
         role = request.user.token.get("role")
         if role == "CUSTOMER":
                 tickets = TicketService.get_tickets_by_customer(request.user.id)

         elif role == "AGENT":
                 tickets = TicketService.get_tickets_by_agent(request.user.id)

         elif role == "ADMIN":
                 tickets = TicketService.get_all_tickets()  

         else:
                 return Response({"message":"unvalid role"},status=status.HTTP_403_FORBIDDEN)                          

         serializer = TicketSerializer(tickets,many=True)
         return Response(serializer.data)


    def post(self,request):
         role = request.user.token.get("role")
         if role  in ['ADMIN','AGENT']:
                 return Response({"message":"CANT CREATE TICKETS"},
                             status=status.HTTP_403_FORBIDDEN)
                 
         serializer = TicketSerializer(data=request.data)
         customer_id = request.user.id
         if not serializer.is_valid():
              return Response({"message":serializer.errors},
                              status=status.HTTP_400_BAD_REQUEST)

         ticket = TicketService.create_ticket(serializer.validated_data,customer_id)

         response_serializer =  TicketSerializer(ticket)

         return Response(response_serializer.data,
                         status = status.HTTP_201_CREATED)
         
class TicketsDeatilView(APIView):
     permission_classes=[IsAuthenticated]

     def get(self,request,ticket_id):
          role = request.user.token.get("role")
          ticket = TicketService.get_ticket(ticket_id)
          print(type(ticket.assigned_agent_id),type(request.user.id),ticket.customer_id,
                role)
          if role == "CUSTOMER" and str(ticket.customer_id) != str(request.user.id):
            return Response({"message":"You dont have permission to "}
                            ,status=status.HTTP_403_FORBIDDEN)
                    
          elif role == "AGENT" and str(ticket.assigned_agent_id) != str(request.user.id):
            return Response({"message":"You dont have permission to "}
                            ,status=status.HTTP_403_FORBIDDEN)

          if role not in ["CUSTOMER","AGENT","ADMIN"] :
                   return Response({"message":"You dont have permission to "}
                                              ,status=status.HTTP_403_FORBIDDEN)
                
          response_serializer = TicketSerializer(ticket)
          return Response(response_serializer.data,
                                   status = status.HTTP_201_CREATED)


     def patch(self,request,ticket_id):
          print(request) 
          ticket = TicketService.get_ticket(ticket_id)
          role = request.user.token.get("role")
          if role == "CUSTOMER" and ticket.customer_id != request.user.id:
                  return Response({"message":"You dont have permission to "}
                                  ,status=status.HTTP_403_FORBIDDEN)
          elif role == "AGENT" and str(ticket.assigned_agent_id) != str(request.user.id):
                            return Response({"message":"You dont have permission to "}
                                            ,status=status.HTTP_403_FORBIDDEN)
          if role == "CUSTOMER":
                  allowed_fields = ["title","decription"]

          elif role == "AGENT":    
                  allowed_fields = ["status"]   

          elif role == "ADMIN":    
                            allowed_fields = ["title",'description',
                                              'status,priority']           

          for field in request.data:
                  if field not in allowed_fields:
                          return Response({"error":"You cannot change this data"}
                                          ,status=status.HTTP_403_FORBIDDEN)
          serializer = TicketSerializer(ticket,data=request.data,partial= True)
          if not serializer.is_valid():
                        return Response({"message":serializer.errors},
                                        status=status.HTTP_400_BAD_REQUEST)

          if "status" in request.data:
                  new_status = request.data["status"]


                  if not TicketService.is_valid_status_transition(
                          ticket.status,
                          new_status
                  ):
                          return Response({"error:":"Invalid status transition"},
                                          status=status.HTTP_400_BAD_REQUEST)                                        
          updated_ticket = TicketService.update_ticket(ticket,serializer.validated_data)

          response_serializer= TicketSerializer(updated_ticket)
          
          return Response(response_serializer.data,
                                             status = status.HTTP_200_OK)

     def delete(self,request,ticket_id):
           ticket = TicketService.get_ticket(ticket_id)
           role = request.user.token.get("role")

           if role == "CUSTOMER" and str(ticket.customer_id) != str(request.user.id):
                   return Response({"message":"You dont have permission to "}
                                    ,status=status.HTTP_403_FORBIDDEN)
           elif role == "AGENT":
                              return Response({"message":"You dont have permission to DELETE your are an egent "}
                                               ,status=status.HTTP_403_FORBIDDEN)
           if role not in ['CUSTOMER','AGENT','ADMIN']:
                    return Response({"message":"You dont have permission to "}
                                     ,status=status.HTTP_403_FORBIDDEN)         
           if ticket is None:
                 return Response({"message":"Ticket not found"}
                                 ,status=status.HTTP_404_NOT_FOUND)
           
           TicketService.delete_ticket(ticket)
           return Response(status=status.HTTP_202_ACCEPTED)
           
class TestView(APIView):
      permission_classes = [IsAuthenticated]

      def get(self,request):
           return Response({
                 "user_id":request.user.id,
                 "role":request.user.token.get("role")
           })  


class AssignAgentView(APIView):
        permission_classes = [IsAuthenticated,IsAdmin]

        def patch(self,request,ticket_id):
                print(request.data)
                print(ticket_id,"ticket")
                ticket = TicketService.get_ticket(ticket_id)
                print(ticket)
                if ticket is None:
                        return Response(
                                {"error":"Ticket not found"},
                                status=status.HTTP_404_NOT_FOUND
                        )
                # ticket_serializer = TicketSerializer(ticket)
                # print(request.data)
                agent_id=request.data.get("agent_id")
                # print("agent_id:", agent_id)

                if agent_id is None:
                        return Response(
                        {"error":"agent is required"},
                         status=status.HTTP_400_BAD_REQUEST
                                        )
                auth_header = request.headers.get("Authorization")
                access_token = auth_header.split(" ")[1]
                try:
                    updated_ticket = TicketService.assign_ticket_to_agent(
                            ticket,
                            agent_id,
                            access_token           
                    )
                    print(updated_ticket,"updated")
                except AuthServiceUnavailable:
                                return Response({"error":"Auth Service is unavailable"},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)


                if updated_ticket is None:
                        return Response(
                        {"error":"No Ticket Found"},
                         status=status.HTTP_400_BAD_REQUEST
                                                        )
                

                response_serializer = TicketSerializer(updated_ticket)

                return Response(
                        response_serializer.data,
                        status=status.HTTP_200_OK
                )
                
              
         

 
