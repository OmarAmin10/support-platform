from django.urls import path
from .views import LoginView, ProfileView, RegisterView, AdminOnlyView,LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/',LoginView.as_view(),name='login'),
    path('profile/<int:user_id>/',ProfileView.as_view(),name='profile'),
    path('register/',RegisterView.as_view(),name='register'),
    path('admin/',AdminOnlyView.as_view(),name='admin'),
    path('refresh/',TokenRefreshView.as_view(),name='token'),
    path('logout/',LogoutView.as_view(),name='logout'),
]