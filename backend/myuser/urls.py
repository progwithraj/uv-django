from django.urls import path
from .views import create_user, get_all_users, get_all_users_by_dept, get_user_details, login_user, logout_user

urlpatterns = [
    path('', get_all_users, name='get_all_users'),
    path('dept/<str:dept>', get_all_users_by_dept, name='get_all_users_by_dept'),
    path('<int:user_id>', get_user_details, name='get_user_details'),
    path('create', create_user, name='create_user'),
    path('login', login_user, name='login_user'),
    path('logout', logout_user, name='logout_user'),
]