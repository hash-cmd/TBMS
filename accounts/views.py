from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def sign_in(request):
	return render(request, 'index.html')

#@login_required(login_url='/')
def login_redirect(request):
	return render(request, 'login_redirect.html')
