from django.urls import path

from .views import TicketsView, TicketsDeatilView,TestView,AssignAgentView

urlpatterns = [
    path('tickets/',TicketsView.as_view(),name='tickets'),
    path('ticket/<int:ticket_id>/',TicketsDeatilView.as_view(),name='ticket'),  
    path('test-auth/',TestView.as_view(),name='test'), 
    path('tickets/<int:ticket_id>/assign/',AssignAgentView.as_view(),name='assign'), 
]