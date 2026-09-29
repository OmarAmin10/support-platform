from .models import Notification
from .serializer import NotificationSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response

class NotificationView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        print(request.user.id)
        notifications = Notification.objects.all()
        notifications = Notification.objects.filter(user_id = request.user.id )

        serializer = NotificationSerializer(notifications,many=True)

        return Response(serializer.data)
    