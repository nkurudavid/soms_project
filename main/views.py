from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash

from account.models import Trainer, Trainee, ProgramManager, Company
from .models import Stack, Cohort


# Create your views here.
def HomePage(request):
    return render(request, 'main/index.html')



# manager views
def ManagerLogin(request):
    if not request.user.is_authenticated or request.user.is_manager!=True:
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_manager==True:
                login(request, user)
                messages.success(request, ('Hi '+user.first_name+', Welcome back to the dashboard!'))
                return redirect(ManagerDashboard)
            else:
                messages.error(request, ('User Email or Password is not correct! Try agin...'))
                return redirect(ManagerLogin)
        else:
            context = {'title': 'Manager Login',}
            return render(request, 'main/accounts/manager/login.html', context)
    else:
        return redirect(ManagerDashboard)


@login_required(login_url='manager_login')
def ManagerLogout(request):
    logout(request)
    messages.info(request, ('You are now Logged out.'))
    return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        # getting stacks
        Stacks = Stack.objects.filter()
        # getting trainers
        Trainers = Trainer.objects.filter()

        context = {
            'title': 'Manager Dashboard', 
            'dash_active': 'active',
            'stack_total': Stacks.count(),
            'trainer_total': Trainers.count(),
        }
        return render(request, 'main/accounts/manager/dashboard.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_profile(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        context = {'title': 'Manager - My Profile', 'profile_active': 'active', }
        return render(request, 'main/accounts/manager/profile.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_team(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        context = {'title': 'Manager - Team', 'team_active': 'active', }
        return render(request, 'main/accounts/manager/team.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_stacks(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        if request.method == 'POST':
            stack_name = request.POST.get("stack_name")
            description = request.POST.get("description")

            if stack_name:
                # stack_name=stack_name.upper()
                found_data = Stack.objects.filter(name=stack_name)
                if found_data:
                    messages.warning(request, "Stack "+stack_name+", Already exist.")
                    return redirect(ManagerDashboard_stacks)
                else:
                    # INSERT DATA IN STACK MODEL
                    add_stack = Stack(
                        name=stack_name, 
                        description=description
                    )
                    add_stack.save()

                    messages.success(request, "New Stack created successfully.")
                    return redirect(ManagerDashboard_stacks)
            else:
                messages.error(request, "Error , Stack name is required!")
                return redirect(ManagerDashboard_stacks)
        else:
            # getting stacks
            Stacks = Stack.objects.filter()
            context = {
                'title': 'Manager - Stacks',
                'stacks_active': 'active', 
                'stacks': Stacks,
                'stack_total': Stacks.count(),
            }
            return render(request, 'main/accounts/manager/stacks.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_stacksEdit(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        stack_id = pk
        # getting stacks
        Stack = Stack.objects.filter(id=stack_id)

        context = {
            'title': 'Manager - Stacks',
            'stacks_active': 'active', 
            'stack': Stack,
        }
        return render(request, 'main/accounts/manager/stacksEdit.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)

