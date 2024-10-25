from django.urls import path
from int_control.views import users, edit_user

urlpatterns = [
    path('users/all/', users, name=""),
    path('edit-user/<str:slug>/', edit_user, name='edit_user'),
]