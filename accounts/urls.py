from django.urls import path
from accounts.views import sign_in, login_redirect

urlpatterns = [
	path('', sign_in, name='login'),
	path('home', login_redirect, name='login_redirect'),
]
