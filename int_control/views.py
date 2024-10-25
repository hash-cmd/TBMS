from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from treasury.models import Branchs
from django.http import JsonResponse


# Create your views here.
@login_required(login_url='/')  
def users(request):
    all_users = CustomUser.objects.all()
    all_branchs = Branchs.objects.all()
    return render(request, 'int_control/users/users.html', {'all_users': all_users, 'all_branchs': all_branchs})



@login_required(login_url='/')  
@require_http_methods(["POST", "PUT"])
def edit_user(request, slug):
    user = get_object_or_404(CustomUser, slug=slug)

    # Get data from the request (POST or PUT)
    data = request.POST if request.method == 'POST' else request.PUT

    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    department = data.get('department')
    branch_code = data.get('branch_code')

    # Validate the form data
    if not username or not email:
        return JsonResponse({'success': False, 'message': 'Username and email are required.'}, status=400)

    # Update the user data
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.department = department
    user.branch_code = branch_code
    user.save()

    return JsonResponse({'success': True, 'message': 'User updated successfully!'})


 