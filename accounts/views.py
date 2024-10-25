from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
def sign_in(request):
	return render(request, 'index.html')

login_required(login_url='/')
def login_redirect(request):
	user = request.user
	if user.department == 'trops':
		return redirect('/trops/')
	elif user.department == 'treasury':
		return redirect('/treasury/')
	elif user.department == 'branch':
		return redirect('/branch/')
	elif user.department == 'admin':
		return redirect('/super/users/all/')
	else:
		return render()