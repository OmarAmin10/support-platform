from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer
from .permissions import IsAdmin
from .models import User
class LoginView(APIView):

    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')


        user = authenticate(username=username,password=password)

        if user is None:
            return Response({"message":"User invalid"}
                            ,status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role

        return Response({
            "message":"Credntials correct",
            "username":user.username,
            "role":user.role,
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]


    def get(self,request,user_id):

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error":"User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "id":user.id,
            "username":user.username,
            "role":user.role,
        })


class RegisterView(APIView):
   

    def post(self,request):
        serializer =  RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        # username = serializer.validated_data.get("username")
        # password = serializer.validated_data.get("password")
        # email = serializer.validated_data.get("email") 
        # user = serializer.create(validated_data=serializer.validated_data)

        user=serializer.save()

        return Response({
            "message":"user created successfully",
            "id":user.id,
            "username":user.username,
            "role":user.role
        },status=status.HTTP_201_CREATED)

    
class AdminOnlyView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    def get(self,request):
        return Response({"message":"only admin"})

class LogoutView(APIView):
    

    def post(self,request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"error":"refresh token required"},
                                        status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"error":"invalid or expired refresh token"},
                            status=status.HTTP_400_BAD_REQUEST)

        
        return Response({"message":"logged out successfully"},
                        status=status.HTTP_200_OK)

    