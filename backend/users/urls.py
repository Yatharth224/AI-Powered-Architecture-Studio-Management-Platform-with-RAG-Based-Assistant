# users/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomLoginView,
    ClientRegisterView,
    LogoutView,
    ProfileView,
    UserListView,
    UpdateUserRoleView,
    InviteArchitectView,
    ArchitectRegisterView,
)

urlpatterns = [
    # Auth
    path('register/client/',      ClientRegisterView.as_view(),    name='client_register'),
    path('register/architect/',   ArchitectRegisterView.as_view(), name='architect_register'),
    path('login/',                CustomLoginView.as_view(),        name='login'),
    path('logout/',               LogoutView.as_view(),             name='logout'),
    path('token/refresh/',        TokenRefreshView.as_view(),       name='token_refresh'),

    # Profile
    path('profile/',              ProfileView.as_view(),            name='profile'),

    # Admin only
    path('users/',                UserListView.as_view(),           name='user_list'),
    path('users/<int:user_id>/role/', UpdateUserRoleView.as_view(), name='update_role'),
    path('invite/architect/',     InviteArchitectView.as_view(),    name='invite_architect'),
]