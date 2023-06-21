from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from datetime import date
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash

from account.models import Trainer, Trainee
from .models import Assignment, AssignmentReport, Group, Feedback, Stack, Cohort, Module, Company
from recruitment.models import Application

import matplotlib.pyplot as plt
import numpy as np
import io
import base64

# Create your views here.
def HomePage(request):
    # getting stacks
    StacksData = Stack.objects.filter()
    TrainersData = Trainer.objects.filter()
    context = {
        'title': 'Welcome to SOMS',
        'courses': StacksData,
        'instructors': TrainersData,
    }
    return render(request, 'home.html', context)


def ApplicationPage(request):
    if request.method == 'POST' :
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        phone1 = request.POST.get('phone1')
        locationAddress = request.POST.get('locationAddress')
        stack = request.POST.get('stack')
        git_link = request.POST.get('git_link')
        more = request.POST.get('more')
        education_level = request.POST.get('education_level')
        cv = request.FILES['cv']
        if not (
            first_name and last_name and email and gender and phone1 and locationAddress and stack and git_link and education_level and cv
        ) : 
            messages.warning(request, "Error , All fields are required.")
            return redirect(ApplicationPage) 
        else :
            #CHECK FOR EXISTING APPLICANT
            if Application.objects.filter(email=email):
                messages.warning(request, "Your application already received.")
                return redirect(ApplicationPage)
            else:
                # GETTING CURRENT STACK
                selectedStack = Stack.objects.get(id=stack)
                # GETTING CURRENT COHORT
                current_cohort = Cohort.objects.latest('starting_date')
                # SUBMITTING APPLICATION
                applicationForm = Application(
                    cohort = current_cohort,
                    stack = selectedStack,
                    first_name = first_name,
                    last_name = last_name,
                    email = email,
                    gender = gender,
                    phone1 = phone1,
                    locationAddress = locationAddress,
                    githubLink = git_link,
                    cv_file = cv,
                    educationLevel = education_level,
                    more = more
                )
                applicationForm.save()

                messages.success(request, "Your Application form has been submitted successfully.")
                return redirect(ApplicationPage)
    else:
        # getting stacks
        StacksData = Stack.objects.filter()
        context = {
            'title': 'Join the BootCamp',
            'courses': StacksData,
        }
        return render(request, 'application.html', context)


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
            return render(request, 'main/manager/login.html', context)
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
        cohorts = Cohort.objects.all()
        stacks = Stack.objects.all()
        data = []

        for cohort in cohorts:
            cohort_trainees = Trainee.objects.filter(cohort=cohort.id)
            stack_counts = {}
            
            for stack in stacks:
                count = cohort_trainees.filter(stack=stack.id).count()
                stack_counts[stack.name] = count

            data.append({
                'cohort_name': cohort.cohort_name,
                'stack_counts': stack_counts
            })


        # getting stacks
        StacksData = Stack.objects.filter()
        # getting trainers
        TrainersData = Trainer.objects.filter()
        # getting new applicants
        current_cohort = Cohort.objects.latest('starting_date')
        NewApplicantsData = Application.objects.filter(cohort=current_cohort.id, status=False)
        # getting cohort
        CohortData = Cohort.objects.filter()
        context = {
            'title': 'Manager Dashboard', 
            'dash_active': 'active', 
            'cohorts': CohortData,
            'stack_total': StacksData.count(),
            'trainer_total': TrainersData.count(),
            'applicant_total': NewApplicantsData.count(),
            'team': TrainersData,
            'data': data
        }
        return render(request, 'main/manager/dashboard.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def Manager_profile(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        if request.method == 'POST':
            old_password = request.POST.get("old_pass")
            new_password = request.POST.get("pass1")
            confirmed_new_password = request.POST.get("pass2")

            if old_password and new_password and confirmed_new_password:
                user = get_user_model().objects.get(email=request.user.email)
                if not user.check_password(old_password):
                    messages.error(request, "Your old password is not correct!")
                    return redirect(Manager_profile)
                else:
                    if len(new_password) < 5:
                        messages.warning(request, "Your password is too weak!")
                        return redirect(Manager_profile)
                    elif new_password != confirmed_new_password:
                        messages.error(request, "Your new password not match the confirm password !")
                        return redirect(Manager_profile)
                    else:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)

                        messages.success(request, "Your password has been changed successfully.!")
                        return redirect(Manager_profile)
            else:
                messages.error(request, "Error , All fields are required !")
                return redirect(Manager_profile)
        else:
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Manager - My Profile',
                'profile_active': 'active',
                'cohorts': CohortData,
            }
            return render(request, 'main/manager/profile.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_team(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        if 'submit' in request.POST:
            # Retrieve the form data from the request
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            phone1 = request.POST.get('phone1')
            phone2 = request.POST.get('phone2')
            specialization = request.POST.get('specialization')
            ssn = request.POST.get('ssn')
            stack = request.POST.get('stack')
            locationAddress = request.POST.get('locationAddress')
            profilePicture = request.FILES.get('profilePicture')

            if first_name and last_name and email and gender and phone1 and phone2 and specialization and ssn and stack and locationAddress and profilePicture:
                if get_user_model().objects.filter(email=email):
                    messages.warning(request, "Email already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(ssn=ssn):
                    messages.warning(request, "SSN already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(phone1=phone1):
                    messages.warning(request, "Phone 1 already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(stack=stack):
                    messages.warning(request, "Stack already assigned.")
                    return redirect(ManagerDashboard_team)
                else:
                    # get stack
                    selectedStack = Stack.objects.get(id=stack)

                    current_year = date.today().year
                    trainerPassword = "trainer"+str(current_year)
                    # Create new User as Trainer
                    user =  get_user_model().objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        gender=gender,
                        is_trainer=True,
                        password=trainerPassword
                    )
                    if user:
                        trainerUser = get_user_model().objects.get(email=email)
                        # Create trainer profile
                        trainerProfile = Trainer(
                            user=trainerUser,
                            stack=selectedStack,
                            ssn=ssn,
                            profilePicture=profilePicture,
                            phone1=phone1,
                            phone2=phone2,
                            specialization=specialization,
                            locationAddress=locationAddress,
                        )
                        trainerProfile.save()
                        messages.success(request, "Trainer "+first_name+", created successfully.")
                        return redirect(ManagerDashboard_team)
                    else:
                        messages.error(request, ('Process Failed.'))
                        return redirect(ManagerDashboard_team)
            else:
                messages.error(request, ('All fields are required.'))
                return redirect(ManagerDashboard_team)
        else:
            # getting team
            teamData = Trainer.objects.filter()
            # getting cohorts
            CohortData = Cohort.objects.filter()
            # getting stacks
            StackData = Stack.objects.filter()

            context = {
                'title': 'Manager - Team',
                'team': teamData,
                'team_total': teamData.count,
                'team_active': 'active',
                'cohorts': CohortData,
                'stacks': StackData,
            }
            return render(request, 'main/manager/team.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_partner(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        if 'submit' in request.POST:
            # Retrieve the form data from the request
            company_name = request.POST.get('company_name')
            locationAddress = request.POST.get('locationAddress')
            logoFile = request.FILES.get('logoFile')

            if company_name and locationAddress and logoFile:
                if Company.objects.filter(name=company_name):
                    messages.warning(request, "Company name already assigned.")
                    return redirect(ManagerDashboard_partner)
                else:
                    # add new company
                    newCompany = Company(
                        name=company_name,
                        location=locationAddress,
                        logoFile=logoFile
                    )
                    newCompany.save()
                    messages.success(request, "Partner "+company_name+", created successfully.")
                    return redirect(ManagerDashboard_partner)
            else:
                messages.error(request, ('All fields are required.'))
                return redirect(ManagerDashboard_partner)
        else:
            # getting cohorts
            CohortData = Cohort.objects.filter()
            # getting companies
            PartnerData = Company.objects.filter()

            context = {
                'title': 'Manager - Partner',
                'partners': PartnerData,
                'partner_active': 'active',
                'cohorts': CohortData,
            }
            return render(request, 'main/manager/partners.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_partnerEdit(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        partner_id = pk
        if Company.objects.filter(id=partner_id).exists():
            # getting partner
            foundData = Company.objects.get(id=partner_id)
            if 'update_product' in request.POST:
                # Retrieve the form data from the request
                company_name = request.POST.get('company_name')
                locationAddress = request.POST.get('locationAddress')

                if company_name and locationAddress:
                    if Company.objects.filter(name=company_name).exclude(id=foundData.id):
                        messages.warning(request, "Company name already assigned.")
                        return redirect(ManagerDashboard_partnerEdit, pk)
                    else:
                        # Update partner
                        updateCompany = Company.objects.filter(id=partner_id).update(
                            name=company_name,
                            location = locationAddress,
                        )
                        if updateCompany:
                            messages.success(request, "Partner "+company_name+", Updated successfully.")
                            return redirect(ManagerDashboard_partnerEdit, pk)
                        else:
                            messages.error(request, ('Process Failed.'))
                            return redirect(ManagerDashboard_partnerEdit, pk)
                else:
                    messages.error(request, ('All fields are required.'))
                    return redirect(ManagerDashboard_partnerEdit, pk)

            if 'update_logo' in request.POST:
                # Retrieve the form data from the request
                logoFile = request.FILES.get('logoFile')

                if logoFile:
                    if len(foundData.logoFile) != 0:
                        foundData.logoFile.delete()

                    # Update partner
                    foundData.logoFile = logoFile
                    foundData.save()

                    messages.success(request, "Partner Updated successfully.")
                    return redirect(ManagerDashboard_partnerEdit, pk)
                else:
                    messages.error(request, ('Company Logo is required.'))
                    return redirect(ManagerDashboard_partnerEdit, pk)

            elif 'delete_partner' in request.POST:
                # Delete Partner
                if len(foundData.logoFile) != 0:
                    foundData.logoFile.delete()
                foundData.delete()
                messages.success(request, "Partner deleted successfully.")
                return redirect(ManagerDashboard_partner)

            else:
                # getting cohorts
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Manager - Partner',
                    'partner': foundData,
                    'partner_active': 'active',
                    'cohorts': CohortData,
                }
                return render(request, 'main/manager/partnerEdit.html', context)
        else:
            messages.error(request, ('Partner not found'))
            return redirect(ManagerDashboard_partner)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_teamEdit(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        trainer_id = pk
        # getting trainer
        if Trainer.objects.filter(id=trainer_id).exists():
            # getting coh
            foundData = Trainer.objects.get(id=trainer_id)
            if foundData:
                trainerData=get_user_model().objects.get(id=foundData.user.id)

            if 'submit' in request.POST:
                # Retrieve the form data from the request
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                gender = request.POST.get('gender')
                phone1 = request.POST.get('phone1')
                phone2 = request.POST.get('phone2')
                specialization = request.POST.get('specialization')
                stack = request.POST.get('stack')
                ssn = request.POST.get('ssn')
                locationAddress = request.POST.get('locationAddress')
                profilePicture = request.FILES.get('profilePicture')

                if first_name and last_name and email and gender and phone1 and phone2 and specialization and ssn and stack and locationAddress:
                    if get_user_model().objects.filter(email=email).exclude(id=foundData.user.id):
                        messages.warning(request, "Email already exist.")
                        return redirect(ManagerDashboard_team)
                    elif Trainer.objects.filter(ssn=ssn).exclude(id=trainer_id):
                        messages.warning(request, "SSN already exist.")
                        return redirect(ManagerDashboard_team)
                    elif Trainer.objects.filter(phone1=phone1).exclude(id=trainer_id):
                        messages.warning(request, "Phone 1 already exist.")
                        return redirect(ManagerDashboard_team)
                    elif Trainer.objects.filter(stack=stack).exclude(id=trainer_id):
                        messages.warning(request, "Stack already assigned.")
                        return redirect(ManagerDashboard_team)
                    else:
                        # get stack
                        selectedStack = Stack.objects.get(id=stack)

                        # Update Trainer account
                        user =  get_user_model().objects.filter(id=foundData.user.id).update(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            gender=gender,
                        )
                        if user:
                            if profilePicture:
                                if len(profilePicture) != 0:
                                    data = Trainer.objects.get(id=trainer_id)
                                    if len(data.profilePicture) != 0:
                                        data.profilePicture.delete()

                                # Update trainer profile
                                data.ssn = ssn
                                data.stack=selectedStack
                                data.profilePicture = profilePicture
                                data.phone1 = phone1
                                data.phone2 = phone2
                                data.specialization = specialization
                                data.locationAddress = locationAddress
                                data.save()
                                updateTrainer = data
                            else:
                                # Update trainer profile
                                updateTrainer = Trainer.objects.filter(id=trainer_id).update(
                                    ssn=ssn,
                                    stack=selectedStack,
                                    phone1=phone1,
                                    phone2=phone2,
                                    specialization=specialization,
                                    locationAddress=locationAddress,
                                )

                            if updateTrainer:
                                messages.success(request, "Trainer "+first_name+", Updated successfully.")
                                return redirect(ManagerDashboard_teamEdit, pk)
                            else:
                                messages.error(request, ('Process Failed.'))
                                return redirect(ManagerDashboard_teamEdit, pk)
                        else:
                            messages.error(request, ('Process Failed.'))
                            return redirect(ManagerDashboard_teamEdit, pk)
                else:
                    messages.error(request, ('All fields are required.'))
                    return redirect(ManagerDashboard_teamEdit, pk)

            elif 'delete' in request.POST:
                # Delete Trainer
                delete_trainer = get_user_model().objects.get(id=foundData.user.id)
                delete_trainer.delete()
                messages.success(request, "Trainer info deleted successfully.")
                return redirect(ManagerDashboard_team)

            else:
                # getting cohorts
                CohortData = Cohort.objects.filter()
                # getting stacks
                StackData = Stack.objects.filter()
                context = {
                    'title': 'Manager - Trainer Info',
                    'team_active': 'active',
                    'profile_data': trainerData,
                    'cohorts': CohortData,
                    'stacks': StackData,
                }
                return render(request, 'main/manager/trainerEdit.html', context)
        else:
            messages.error(request, ('Trainer not found'))
            return redirect(ManagerDashboard_team)
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
                    # add new stack
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
            StackData = Stack.objects.filter()
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Manager - Stacks',
                'stacks_active': 'active', 
                'stacks': StackData, 
                'cohorts': CohortData,
                'stack_total': StackData.count(),
            }
            return render(request, 'main/manager/stacks.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_stackEdit(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        stack_id = pk
        # getting stack
        if Stack.objects.filter(id=stack_id).exists():
            # if exists
            foundData = Stack.objects.get(id=stack_id)

            if 'submit' in request.POST:
                # Retrieve the form data from the request
                stack_name = request.POST.get('stack_name')
                description = request.POST.get('description')

                if stack_name :
                    if Stack.objects.filter(name=stack_name).exclude(id=stack_id):
                        messages.warning(request, "Stack name already exist.")
                        return redirect(ManagerDashboard_stacks)
                    else:
                        # Update Stack
                        stack_updated =  Stack.objects.filter(id=stack_id).update(
                            name=stack_name,
                            description=description
                        )
                        if stack_updated:
                            messages.success(request, "Stack "+stack_name+", Updated successfully.")
                            return redirect(ManagerDashboard_stacks)
                        else:
                            messages.error(request, ('Process Failed.'))
                            return redirect(ManagerDashboard_stacks)
                else:
                    messages.error(request, ('Stack name is required.'))
                    return redirect(ManagerDashboard_stacks)

            elif 'delete' in request.POST:
                # Delete Stack
                delete_stack = Stack.objects.get(id=stack_id)
                delete_stack.delete()
                messages.success(request, "Stack info deleted successfully.")
                return redirect(ManagerDashboard_stacks)

            else:
                # getting cohort
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Manager - Stack Info',
                    'stacks_active': 'active',
                    'stack': foundData,
                    'cohorts': CohortData,
                }
                return render(request, 'main/manager/stackEdit.html', context)
        else:
            messages.error(request, ('Stack not found'))
            return redirect(ManagerDashboard_stacks)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_cohorts(request):
    if request.user.is_authenticated and request.user.is_manager==True:
        if request.method == 'POST':
            cohort_name = request.POST.get("cohort_name")
            starting_date = request.POST.get("starting_date")
            ending_date = request.POST.get("ending_date")

            if cohort_name and starting_date and ending_date:
                # stack_name=stack_name.upper()
                found_data = Cohort.objects.filter(cohort_name=cohort_name)
                if found_data:
                    messages.warning(request, "Cohort "+cohort_name+", Already exist.")
                    return redirect(ManagerDashboard_cohorts)
                else:
                    # Create new Cohort
                    add_cohort = Cohort(
                        cohort_name=cohort_name,
                        starting_date=starting_date,
                        ending_date=ending_date
                    )
                    add_cohort.save()

                    messages.success(request, "New Cohort created successfully.")
                    return redirect(ManagerDashboard_cohorts)
            else:
                messages.error(request, "Error , All fields are required!")
                return redirect(ManagerDashboard_cohorts)
        else:
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Manager - Cohorts',
                'cohort_active': 'active',
                'cohorts': CohortData,
                'cohort_total': CohortData.count(),
            }
            return render(request, 'main/manager/cohorts.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def ManagerDashboard_cohortEdit(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        cohort_id = pk
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            foundData = Cohort.objects.get(id=cohort_id)

            if 'submit' in request.POST:
                # Retrieve the form data from the request
                cohort_name = request.POST.get("cohort_name")
                starting_date = request.POST.get("starting_date")
                ending_date = request.POST.get("ending_date")

                if cohort_name and starting_date and ending_date:
                    if Cohort.objects.filter(cohort_name=cohort_name).exclude(id=cohort_id):
                        messages.warning(request, "Cohort name already exist.")
                        return redirect(ManagerDashboard_cohorts)
                    else:
                        # Update Cohort
                        updated_cohort =  Cohort.objects.filter(id=cohort_id).update(
                            cohort_name=cohort_name,
                            starting_date=starting_date,
                            ending_date=ending_date
                        )
                        if updated_cohort:
                            messages.success(request, "Cohort "+cohort_name+", Updated successfully.")
                            return redirect(ManagerDashboard_cohorts)
                        else:
                            messages.error(request, ('Process Failed.'))
                            return redirect(ManagerDashboard_cohorts)
                else:
                    messages.error(request, ('All fields are required.'))
                    return redirect(ManagerDashboard_cohorts)

            elif 'delete' in request.POST:
                # Delete Cohort
                delete_cohort = Cohort.objects.get(id=cohort_id)
                delete_cohort.delete()
                messages.success(request, "Cohort info deleted successfully.")
                return redirect(ManagerDashboard_cohorts)

            else:
                # getting cohort
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Manager - Cohort Info',
                    'cohorts_active': 'active',
                    'cohort': foundData,
                    'cohorts': CohortData,
                }
                return render(request, 'main/manager/cohortEdit.html', context)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(ManagerDashboard_cohorts)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_applicationList(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        cohort_id = pk
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            # Get Application with cohort.id = pk
            applicantsData = Application.objects.filter(cohort=cohort_id).order_by('status')
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Manager - Applicants',
                'application_active': 'active',
                'current_cohort': current_cohort,
                'cohorts': CohortData,
                'applicants': applicantsData,
                'applicant_total': applicantsData.count
            }
            return render(request, 'main/manager/application_list.html', context)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(ManagerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_applicationDetails(request, pk, n):
    if request.user.is_authenticated and request.user.is_manager==True:
        cohort_id = pk
        applicant_id = n
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            if Application.objects.filter(id=applicant_id).exists():
                # get applicant
                applicant = Application.objects.get(id=applicant_id)

                if 'approved' in request.POST:
                    current_year = date.today().year
                    traineePassword = "trainee"+str(current_year)
                    # create a new trainee account
                    user =  get_user_model().objects.create_user(
                        first_name=applicant.first_name,
                        last_name=applicant.last_name,
                        gender=applicant.gender,
                        email=applicant.email,
                        is_trainee=True,
                        password=traineePassword
                    )
                    if user:
                        traineeUser = get_user_model().objects.get(email=applicant.email)
                        # Create trainee profile
                        traineeProfile = Trainee(
                            user=traineeUser,
                            cohort=applicant.cohort,
                            stack=applicant.stack,
                            git_account=applicant.githubLink,
                            phone1=applicant.phone1,
                            locationAddress=applicant.locationAddress,
                            cv_document=applicant.cv_file.url,
                            status='Pending',
                        )
                        traineeProfile.save()

                        # update application status
                        applicant.status=True
                        applicant.save()

                        # SENDING NOTIFICATION TO APPLICANT THROUGH AN EMAIL
                        subject = 'Congratulations! Your Application Accepted'
                        message = 'Dear '+applicant.first_name+' '+applicant.last_name+',\n\n Great news! We are pleased to inform you that your application for '+current_cohort.cohort_name+', in stack '+applicant.stack.name+' has been accepted. You stood out among the applicants with your exceptional qualifications and potential.\n\n Please find attached important details and next steps. Feel free to reach out if you have any questions.\n\n Your login credential account are email: '+applicant.email+', password: '+traineePassword+'. Congratulations once again on your acceptance!\n\n Best regards,\n\n SOMS'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list =[applicant.email,]
                        send_mail( subject, message, email_from, recipient_list )

                        messages.success(request, "Application approved successfully.")
                        return redirect(ManagerDashboard_applicationList, pk)
                    else:
                        messages.error(request, ('Process Failed.'))
                        return redirect(ManagerDashboard_applicationList, pk)

                elif 'rejected' in request.POST:
                    if len(applicant.cv_file )  > 0:
                        applicant.cv_file.delete()
                    # Delete Application
                    applicant.delete()

                    # SENDING NOTIFICATION TO APPLICANT THROUGH AN EMAIL
                    subject = 'Application Status Update - Regretful Decision'
                    message = 'Dear '+applicant.first_name+' '+applicant.last_name+',\n\n We regret to inform you that your application for '+current_cohort.cohort_name+', in '+applicant.stack.name+' has been unsuccessful. The selection process was highly competitive, and although your application showed promise, we had to make difficult decisions based on our specific criteria and available opportunities.\n\n While we are unable to provide detailed feedback, we encourage you to explore other options and continue pursuing your goals. Keep an eye out for future opportunities with our organization, as your qualifications may align with upcoming openings.\n\n Thank you for your interest in SOMS. We wish you all the best in your future endeavors.\n\n Sincerely,\n\n SOMS'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list =[applicant.email,]
                    send_mail( subject, message, email_from, recipient_list )

                    messages.success(request, "Application rejected successfully.")
                    return redirect(ManagerDashboard_applicationList, pk)

                else:
                    # getting cohort
                    CohortData = Cohort.objects.filter()
                    context = {
                        'title': 'Manager - Applicant Details',
                        'application_active': 'active',
                        'current_cohort': current_cohort,
                        'cohorts': CohortData,
                        'applicant': applicant,
                    }
                    return render(request, 'main/manager/application_details.html', context)
            else:
                messages.error(request, ('Application not found'))
                return redirect(ManagerDashboard_applicationList, pk)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(ManagerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_traineesList(request, pk):
    if request.user.is_authenticated and request.user.is_manager==True:
        cohort_id = pk
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            # getting all trainees from cohort
            traineesData=Trainee.objects.filter(cohort=pk).order_by('stack')
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Manager - Trainees',
                'trainees_active': 'active',
                'current_cohort': current_cohort,
                'cohorts': CohortData,
                'trainees': traineesData,
                'trainees_total': traineesData.count
            }
            return render(request, 'main/manager/trainees_list.html', context)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(ManagerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)



@login_required(login_url='manager_login')
def ManagerDashboard_traineeProfile(request, pk, n):
    if request.user.is_authenticated and request.user.is_manager==True:
        cohort_id = pk
        trainee_id = n
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            if Trainee.objects.filter(id=trainee_id).exists():
                # get trainee
                trainee = Trainee.objects.get(id=trainee_id)
                if 'dismiss' in request.POST:
                    if trainee.cv_document:
                        if len(trainee.cv_document )  > 0:
                            trainee.cv_document.delete()
                    # Delete Trainee
                    get_user_model().objects.filter(id=trainee.user.id).delete()
                    Application.objects.filter(email=trainee.user.email).delete()
                    messages.success(request, "Trainee dismissed successfully.")
                    return redirect(ManagerDashboard_traineesList, pk)
                else:
                    # getting cohort
                    CohortData = Cohort.objects.filter()
                    context = {
                        'title': 'Manager - Trainee Profile',
                        'trainees_active': 'active',
                        'current_cohort': current_cohort,
                        'cohorts': CohortData,
                        'trainee': trainee,
                    }
                    return render(request, 'main/manager/trainees_profile.html', context)
            else:
                messages.error(request, ('Trainee Profile not found'))
                return redirect(ManagerDashboard_traineesList, pk)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(ManagerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)





# trainer views
def TrainerLogin(request):
    if not request.user.is_authenticated or request.user.is_trainer!=True:
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_trainer==True:
                login(request, user)
                messages.success(request, ('Hi '+user.first_name+', Welcome back to the dashboard!'))
                return redirect(TrainerDashboard)
            else:
                messages.error(request, ('User Email or Password is not correct! Try agin...'))
                return redirect(TrainerLogin)
        else:
            context = {'title': 'Trainer Login',}
            return render(request, 'main/trainer/login.html', context)
    else:
        return redirect(TrainerDashboard)


@login_required(login_url='trainer_login')
def TrainerLogout(request):
    logout(request)
    messages.info(request, ('You are now Logged out.'))
    return redirect(TrainerLogin)


@login_required(login_url='trainer_login')
def TrainerDashboard(request):
    if request.user.is_authenticated and request.user.is_trainer==True:
        # getting current cohort
        currCohort = Cohort.objects.all().order_by('-starting_date').first()
        # getting trainees
        TraineesData = Trainee.objects.filter(cohort=currCohort, stack=request.user.trainers.stack)
        # getting Modules
        ModulesData = Module.objects.filter(stack=request.user.trainers.stack)
        # getting cohort
        CohortData = Cohort.objects.filter()
        context = {
            'title': 'Trainer Dashboard', 
            'dash_active': 'active', 
            'cohorts': CohortData,
            'current_cohort': currCohort,
            'module_total': ModulesData.count(),
            'trainee_total': TraineesData.count(),
        }
        return render(request, 'main/trainer/dashboard.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)


@login_required(login_url='trainer_login')
def Trainer_profile(request):
    if request.user.is_authenticated and request.user.is_trainer==True:
        if request.method == 'POST':
            old_password = request.POST.get("old_pass")
            new_password = request.POST.get("pass1")
            confirmed_new_password = request.POST.get("pass2")

            if old_password and new_password and confirmed_new_password:
                user = get_user_model().objects.get(email=request.user.email)
                if not user.check_password(old_password):
                    messages.error(request, "Your old password is not correct!")
                    return redirect(Trainer_profile)
                else:
                    if len(new_password) < 5:
                        messages.warning(request, "Your password is too weak!")
                        return redirect(Trainer_profile)
                    elif new_password != confirmed_new_password:
                        messages.error(request, "Your new password not match the confirm password !")
                        return redirect(Trainer_profile)
                    else:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)

                        messages.success(request, "Your password has been changed successfully.!")
                        return redirect(Trainer_profile)
            else:
                messages.error(request, "Error , All fields are required !")
                return redirect(Trainer_profile)
        else:
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Trainer - My Profile',
                'profile_active': 'active',
                'cohorts': CohortData,
            }
            return render(request, 'main/trainer/profile.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)


@login_required(login_url='trainer_login')
def TrainerDashboard_traineeList(request, pk):
    if request.user.is_authenticated and request.user.is_trainer==True:
        cohort_id = pk
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            if request.POST:
                group_name = request.POST.get("name")
                if group_name:
                    # check existing module
                    if Group.objects.filter(cohort=current_cohort, stack=request.user.trainers.stack, group_name=group_name):
                        messages.warning(request, group_name+" already exist.")
                        return redirect(TrainerDashboard_traineeList, pk)
                    else:
                        # add new stack
                        newGroup = Group(
                            cohort=current_cohort,
                            stack=request.user.trainers.stack,
                            group_name=group_name
                        )
                        newGroup.save()

                        messages.success(request, "New Group created successfully.")
                        return redirect(TrainerDashboard_traineeList, pk)
                else:
                    messages.error(request, "Error , Group required!")
                    return redirect(TrainerDashboard_traineeList, pk)
            else:
                # getting all trainees from cohort
                traineesData=Trainee.objects.filter(cohort=pk, stack=request.user.trainers.stack)
                # getting group
                groupData = Group.objects.filter(cohort=pk, stack=request.user.trainers.stack).annotate(trainee_count=Count('trainees'))
                # getting cohort
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Trainer - Trainees List',
                    'trainees_active': 'active',
                    'current_cohort': current_cohort,
                    'cohorts': CohortData,
                    'groups': groupData,
                    'trainees': traineesData,
                    'trainees_total': traineesData.count
                }
                return render(request, 'main/trainer/trainees_list.html', context)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(TrainerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)




@login_required(login_url='trainer_login')
def TrainerDashboard_groupEdit(request, pk, g):
    if request.user.is_authenticated and request.user.is_trainer==True:
        cohort_id = pk
        group_id = g
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            # getting group
            if Group.objects.filter(id=group_id).exists():
                # if exists
                selectedGroup = Group.objects.get(id=group_id, stack=request.user.trainers.stack)
                if 'update_group' in request.POST:
                    group_name = request.POST.get("name")
                    if group_name:
                        # check existing module
                        if Group.objects.filter(cohort=current_cohort, stack=request.user.trainers.stack, group_name=group_name).exclude(id=group_id):
                            messages.warning(request, group_name+" already exist.")
                            return redirect(TrainerDashboard_groupEdit, pk, g)
                        else:
                            # Update Group
                            updateModule = Group.objects.filter(id=group_id, cohort=current_cohort, stack=request.user.trainers.stack).update(
                                group_name=group_name
                            )
                            if updateModule:
                                messages.success(request, "Group updated successfully.")
                                return redirect(TrainerDashboard_groupEdit, pk, g)
                            else:
                                messages.error(request, ('Process Failed.'))
                                return redirect(TrainerDashboard_groupEdit, pk, g)
                    else:
                        messages.error(request, "Error , Group required!")
                        return redirect(TrainerDashboard_groupEdit, pk, g)

                elif 'delete' in request.POST:
                    # Delete Group
                    selectedGroup.delete()
                    messages.success(request, "Group deleted successfully.")
                    return redirect(TrainerDashboard_traineeList, pk)

                elif 'submitMembers' in request.POST:
                    trainee_ids = request.POST.getlist('trainees')

                    for trainee_id in trainee_ids:
                        trainee = Trainee.objects.get(id=trainee_id, cohort=pk, stack=request.user.trainers.stack)
                        trainee.group = selectedGroup
                        trainee.save()

                    messages.success(request, "Group members added successfully.")
                    return redirect(TrainerDashboard_groupEdit, pk, g)

                elif 'remove_member' in request.POST:
                    member_id = request.POST.get("member")
                    trainee = Trainee.objects.get(id=member_id, cohort=pk, stack=request.user.trainers.stack)
                    if trainee.group == selectedGroup:
                        trainee.group = None
                        trainee.save()
                    messages.success(request, "Member removed successfully.")
                    return redirect(TrainerDashboard_groupEdit, pk, g)

                else:
                    # getting all trainees from cohort whose group is null
                    traineesData=Trainee.objects.filter(cohort=pk, stack=request.user.trainers.stack, group__isnull=True)
                    # getting cohort
                    CohortData = Cohort.objects.filter()
                    context = {
                        'title': 'Trainer - Groups',
                        'trainees_active': 'active',
                        'current_cohort': current_cohort,
                        'cohorts': CohortData,
                        'trainees': traineesData,
                        'selectedGroup': selectedGroup,
                        # 'groupMembers': selectedGroup.count
                    }
                    return render(request, 'main/trainer/groupEdit.html', context)
            else:
                messages.error(request, ('Group not found'))
                return redirect(TrainerDashboard_traineeList, pk)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(TrainerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='manager_login')
def TrainerDashboard_traineeProfile(request, pk, n):
    if request.user.is_authenticated and request.user.is_trainer==True:
        cohort_id = pk
        trainee_id = n
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            if Trainee.objects.filter(id=trainee_id, stack=request.user.trainers.stack).exists():
                # get trainee
                trainee = Trainee.objects.get(id=trainee_id)
                # getting cohort
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Trainer - Trainee Profile',
                    'trainees_active': 'active',
                    'current_cohort': current_cohort,
                    'cohorts': CohortData,
                    'trainee': trainee,
                }
                return render(request, 'main/trainer/trainees_profile.html', context)
            else:
                messages.error(request, ('Trainee Profile not found'))
                return redirect(TrainerDashboard_traineeList, pk)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(TrainerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='trainer_login')
def TrainerDashboard_module(request):
    if request.user.is_authenticated and request.user.is_trainer==True:
        if 'new_module' in request.POST:
            module_name = request.POST.get("module_name")
            description = request.POST.get("description")
            notes_document = request.FILES.get('notes_document')

            if module_name:
                # check existing module
                if Module.objects.filter(name=module_name, stack=request.user.trainers.stack):
                    messages.warning(request, "Module "+module_name+", Already exist.")
                    return redirect(TrainerDashboard_module)
                else:
                    # add new stack
                    new_module = Module(
                        stack=request.user.trainers.stack,
                        name=module_name, 
                        description=description,
                        documentFiles=notes_document
                    )
                    new_module.save()

                    messages.success(request, "New Module registered successfully.")
                    return redirect(TrainerDashboard_module)
            else:
                messages.error(request, "Error , Module required!")
                return redirect(TrainerDashboard_module)
        else:
            # getting modules
            ModuleData = Module.objects.filter(stack=request.user.trainers.stack)
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Trainer - Modules',
                'modules_active': 'active', 
                'cohorts': CohortData,
                'modules': ModuleData,
                'module_total': ModuleData.count(),
            }
            return render(request, 'main/trainer/modules.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='trainer_login')
def TrainerDashboard_moduleEdit(request, pk):
    if request.user.is_authenticated and request.user.is_trainer==True:
        module_id = pk
        if Module.objects.filter(id=module_id, stack=request.user.trainers.stack).exists():
            # getting module
            moduleData = Module.objects.get(id=module_id, stack=request.user.trainers.stack)

            if 'submit' in request.POST:
                module_name = request.POST.get("module_name")
                description = request.POST.get("description")
                notes_document = request.FILES.get('notes_document')

                if module_name:
                    # check existing module
                    if Module.objects.filter(name=module_name, stack=request.user.trainers.stack).exclude(id=module_id):
                        messages.warning(request, "Module "+module_name+", Already exist.")
                        return redirect(TrainerDashboard_moduleEdit, pk)
                    else:
                        if notes_document:
                            if len(notes_document) != 0:
                                # check if existing module have document
                                if len(moduleData.documentFiles) != 0:
                                    moduleData.documentFiles.delete()

                            # Update module with document file
                            moduleData.name=module_name, 
                            moduleData.description=description,
                            moduleData.documentFiles=notes_document
                            # save changes
                            moduleData.save()
                            updateModule = moduleData
                        else:
                            # Update Module
                            updateModule = Module.objects.filter(id=module_id, stack=request.user.trainers.stack).update(
                                name=module_name, 
                                description=description,
                            )

                        if updateModule:
                            messages.success(request, "Module "+module_name+", Updated successfully.")
                            return redirect(TrainerDashboard_moduleEdit, pk)
                        else:
                            messages.error(request, ('Process Failed.'))
                            return redirect(TrainerDashboard_moduleEdit, pk)
                else:
                    messages.error(request, ('All fields are required.'))
                    return redirect(TrainerDashboard_moduleEdit, pk)

            elif 'delete' in request.POST:
                # Delete Module and it's files
                if len(moduleData.documentFiles) != 0:
                    moduleData.documentFiles.delete()
                moduleData.delete()
                messages.success(request, "Module deleted successfully.")
                return redirect(TrainerDashboard_module)

            else:
                # getting cohorts
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Trainer - Module Info',
                    'modules_active': 'active',
                    'cohorts': CohortData,
                    'module': moduleData,
                }
                return render(request, 'main/trainer/moduleEdit.html', context)
        else:
            messages.error(request, ('Module not found'))
            return redirect(TrainerDashboard_module)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='trainer_login')
def TrainerDashboard_assignmentList(request, pk):
    if request.user.is_authenticated and request.user.is_trainer==True:
        cohort_id = pk
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            # getting current assignment
            currentAssignment = Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack).order_by('-createdDate').first()
            if 'submit' in request.POST:
                # Retrieve the form data from the request
                title = request.POST.get('title')
                description = request.POST.get('description')
                documentFiles = request.FILES.get('documentFiles')
                startDate = request.POST.get('start_date')
                due_date = request.POST.get('due_date')

                if title and description and startDate and due_date:
                    if Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack,title=title):
                        messages.warning(request, "Assignment title exist.")
                        return redirect(TrainerDashboard_assignmentList, pk)
                    else:
                        if documentFiles:
                            # create assignment
                            newAssignment = Assignment(
                                cohort=current_cohort,
                                stack=request.user.trainers.stack,
                                title=title,
                                description=description,
                                documentFiles=documentFiles,
                                startDate=startDate,
                                dueDate=due_date,
                            )
                            newAssignment.save()
                        else:
                            # create assignment
                            newAssignment = Assignment(
                                cohort=current_cohort,
                                stack=request.user.trainers.stack,
                                title=title,
                                description=description,
                                startDate=startDate,
                                dueDate=due_date,
                            )
                            newAssignment.save()
                        messages.success(request, "Assignment created successfully.")
                        return redirect(TrainerDashboard_assignmentList, pk)
                else:
                    messages.error(request, ('All fields are required.'))
                    return redirect(TrainerDashboard_assignmentList, pk)
            else:
                # getting group
                groupData = Group.objects.filter(cohort=pk, stack=request.user.trainers.stack).annotate(trainee_count=Count('trainees'))
                # getting assignments
                assignmentData = Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack).order_by('-createdDate')
                # getting assignment reports
                reportData = AssignmentReport.objects.filter(assignment=currentAssignment).order_by('-createdDate')
                # getting modules
                moduleData = Module.objects.filter(stack=request.user.trainers.stack)
                # getting cohorts
                CohortData = Cohort.objects.filter()

                context = {
                    'title': 'Trainer - Assignment',
                    'assignment_active': 'active',
                    'groups': groupData,
                    'assignments': assignmentData,
                    'reports': reportData,
                    'assignments_total': assignmentData.count,
                    'modules': moduleData,
                    'cohorts': CohortData,
                    'current_cohort': current_cohort
                }
                return render(request, 'main/trainer/assignmentList.html', context)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(TrainerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='trainer_login')
def TrainerDashboard_assignmentEdit(request, pk, n):
    if request.user.is_authenticated and request.user.is_trainer==True:
        cohort_id = pk
        assignment_id = n
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            if Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack, id=assignment_id).exists():
                # if exists
                selectedAssignment = Assignment.objects.get(cohort=pk, stack=request.user.trainers.stack, id=assignment_id)
                if 'submit' in request.POST:
                    # Retrieve the form data from the request
                    title = request.POST.get('title')
                    description = request.POST.get('description')
                    documentFiles = request.FILES.get('documentFiles')
                    start_date = request.POST.get('start_date')
                    due_date = request.POST.get('due_date')

                    if title and description and start_date and due_date:
                        if Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack,title=title).exclude(id=assignment_id):
                            messages.warning(request, "Assignment title exist.")
                            return redirect(TrainerDashboard_assignmentList, pk)
                        else:
                            if documentFiles:
                                if selectedAssignment.documentFiles:
                                    # check if existing assignment have document
                                    if len(selectedAssignment.documentFiles) != 0:
                                        selectedAssignment.documentFiles.delete()

                                # Update assignment with document file
                                updateAssignment = Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack, id=assignment_id).update(
                                    title=title, 
                                    description=description,
                                    documentFiles=documentFiles,
                                    startDate=start_date,
                                    dueDate=due_date,
                                )
                            else:
                                # Update assignment
                                updateAssignment = Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack, id=assignment_id).update(
                                    title=title, 
                                    description=description,
                                    startDate=start_date,
                                    dueDate=due_date,
                                )

                            if updateAssignment:
                                messages.success(request, "Assignment updated successfully.")
                                return redirect(TrainerDashboard_assignmentEdit, pk, n)
                            else:
                                messages.error(request, ('Process Failed.'))
                                return redirect(TrainerDashboard_assignmentEdit, pk, n)
                    else:
                        messages.error(request, ('All fields are required.'))
                        return redirect(TrainerDashboard_assignmentEdit, pk, n)

                elif 'is_marked' in request.POST:
                    # Update assignment status
                    updateAssignment = Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack, id=assignment_id).update(
                        status=True
                    )
                    return redirect(TrainerDashboard_assignmentEdit, pk, n)

                elif 'ongoing' in request.POST:
                    # Update assignment status
                    updateAssignment = Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack, id=assignment_id).update(
                        status=False
                    )
                    return redirect(TrainerDashboard_assignmentEdit, pk, n)

                elif 'delete' in request.POST:
                    # Delete Assignment file
                    if selectedAssignment.documentFiles:
                        if len(selectedAssignment.documentFiles) != 0:
                            selectedAssignment.documentFiles.delete()
                    # Delete Assignment
                    selectedAssignment.delete()
                    messages.success(request, "Assignment deleted successfully.")
                    return redirect(TrainerDashboard_assignmentList, pk)

                else:
                    # getting group
                    groupData = Group.objects.filter(cohort=pk, stack=request.user.trainers.stack).annotate(trainee_count=Count('trainees'))
                    # getting assignment reports
                    reportData = AssignmentReport.objects.filter(assignment=selectedAssignment).order_by('-createdDate')
                    # getting cohorts
                    CohortData = Cohort.objects.filter()

                    context = {
                        'title': 'Trainer - Assignment Info',
                        'assignment_active': 'active',
                        'current_cohort': current_cohort,
                        'cohorts': CohortData,
                        'assignment': selectedAssignment,
                        'reports': reportData,
                        'groups': groupData,
                    }
                    return render(request, 'main/trainer/assignmentEdit.html', context)
            else:
                messages.error(request, ('Assignment not found'))
                return redirect(TrainerDashboard_assignmentList, pk)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(TrainerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='trainer_login')
def TrainerDashboard_reportCollection(request, pk, n, k):
    if request.user.is_authenticated and request.user.is_trainer==True:
        cohort_id = pk
        assignment_id = n
        report_id = k
        # getting cohort
        if Cohort.objects.filter(id=cohort_id).exists():
            # if exists
            current_cohort = Cohort.objects.get(id=cohort_id)
            if Assignment.objects.filter(cohort=pk, stack=request.user.trainers.stack, id=assignment_id).exists():
                # if exists
                selectedAssignment = Assignment.objects.get(cohort=pk, stack=request.user.trainers.stack, id=assignment_id)
                if AssignmentReport.objects.filter(id=report_id, assignment=assignment_id).exists():
                    # if exists
                    reportData = AssignmentReport.objects.get(id=report_id, assignment=assignment_id)
                    if 'submit' in request.POST:
                        # Retrieve the form data from the request
                        grade = request.POST.get('grade')
                        comment = request.POST.get('comment')

                        if grade and comment:
                            # create feedback
                            reportFeedback = Feedback(
                                report =reportData,
                                grade =grade,
                                comment =comment
                            )
                            reportFeedback.save()
                            # update assignment report status to true for marked
                            AssignmentReport.objects.filter(id=report_id, assignment=assignment_id).update(
                                status=True,
                            )
                            messages.success(request, "Report graded successfully.")
                            return redirect(TrainerDashboard_reportCollection, pk, n, k)
                        else:
                            messages.error(request, ('All fields are required.'))
                            return redirect(TrainerDashboard_reportCollection, pk, n, k)

                    elif 'update_comment' in request.POST:
                        # Retrieve the form data from the request
                        grade = request.POST.get('grade')
                        comment = request.POST.get('comment')

                        if grade and comment:
                            # update feedback
                            Feedback.objects.filter(report=report_id).update(
                                grade =grade,
                                comment =comment
                            )
                            messages.success(request, "Report graded successfully.")
                            return redirect(TrainerDashboard_reportCollection, pk, n, k)
                        else:
                            messages.error(request, ('All fields are required.'))
                            return redirect(TrainerDashboard_reportCollection, pk, n, k)

                    else:
                        # getting cohorts
                        CohortData = Cohort.objects.filter()
                        context = {
                            'title': 'Trainer - Assignment Report Info',
                            'assignment_active': 'active',
                            'cohorts': CohortData,
                            'current_cohort': current_cohort,
                            'assignment': selectedAssignment,
                            'report': reportData,
                        }
                        return render(request, 'main/trainer/reportCollection.html', context)
                else:
                    messages.error(request, ('report not found'))
                    return redirect(TrainerDashboard_assignmentEdit, pk, n)
            else:
                messages.error(request, ('Assignment not found'))
                return redirect(TrainerDashboard_assignmentList, pk)
        else:
            messages.error(request, ('Cohort not found'))
            return redirect(TrainerDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)






# trainee views
def TraineeLogin(request):
    if not request.user.is_authenticated or request.user.is_trainee!=True:
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_trainee==True:
                login(request, user)
                messages.success(request, ('Hi '+user.first_name+', Welcome back to the dashboard!'))
                return redirect(TraineeDashboard)
            else:
                messages.error(request, ('User Email or Password is not correct! Try agin...'))
                return redirect(TraineeLogin)
        else:
            context = {'title': 'Trainee Login',}
            return render(request, 'main/trainee/login.html', context)
    else:
        return redirect(TraineeDashboard)


@login_required(login_url='trainee_login')
def TraineeLogout(request):
    logout(request)
    messages.info(request, ('You are now Logged out.'))
    return redirect(TraineeLogin)


@login_required(login_url='trainee_login')
def TraineeDashboard(request):
    if request.user.is_authenticated and request.user.is_trainee==True:
        # getting modules
        modulesData = Module.objects.filter(stack=request.user.trainees.stack)
        # getting assignments
        assignmentData = Assignment.objects.filter(stack=request.user.trainees.stack, status=False).order_by('-createdDate')
        # getting trainees
        traineesData = Trainee.objects.filter(stack=request.user.trainees.stack)
        context = {
            'title': 'Trainee Dashboard', 
            'dash_active': 'active',
            'modules': modulesData,
            'module_total': modulesData.count(),
            'assignments': assignmentData,
            'trainees': traineesData,
        }
        return render(request, 'main/trainee/dashboard.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TraineeLogin)


@login_required(login_url='trainee_login')
def Trainee_profile(request):
    if request.user.is_authenticated and request.user.is_trainee==True:
        if request.method == 'POST':
            old_password = request.POST.get("old_pass")
            new_password = request.POST.get("pass1")
            confirmed_new_password = request.POST.get("pass2")

            if old_password and new_password and confirmed_new_password:
                user = get_user_model().objects.get(email=request.user.email)
                if not user.check_password(old_password):
                    messages.error(request, "Your old password is not correct!")
                    return redirect(Trainee_profile)
                else:
                    if len(new_password) < 5:
                        messages.warning(request, "Your password is too weak!")
                        return redirect(Trainee_profile)
                    elif new_password != confirmed_new_password:
                        messages.error(request, "Your new password not match the confirm password !")
                        return redirect(Trainee_profile)
                    else:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)

                        messages.success(request, "Your password has been changed successfully.!")
                        return redirect(Trainee_profile)
            else:
                messages.error(request, "Error , All fields are required !")
                return redirect(Trainee_profile)
        else:
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Trainee - My Profile',
                'profile_active': 'active',
                'cohorts': CohortData,
            }
            return render(request, 'main/trainee/profile.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TraineeLogin)


@login_required(login_url='trainee_login')
def TraineeDashboard_moduleInfo(request, pk):
    if request.user.is_authenticated and request.user.is_trainee==True:
        module_id = pk
        if Module.objects.filter(id=module_id, stack=request.user.trainees.stack).exists():
            # getting module
            moduleData = Module.objects.get(id=module_id, stack=request.user.trainees.stack)
            context = {
                'title': 'Trainee - Module Info',
                'modules_active': 'active',
                'module': moduleData,
            }
            return render(request, 'main/trainee/moduleInfo.html', context)
        else:
            messages.error(request, ('Module not found'))
            return redirect(TraineeDashboard)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TraineeLogin)


@login_required(login_url='trainee_login')
def TraineeDashboard_assignmentList(request):
    if request.user.is_authenticated and request.user.is_trainee==True:
        # getting current assignment
        assignmentData = Assignment.objects.filter(stack=request.user.trainees.stack).order_by('-createdDate')
        groupData = Group.objects.filter(id=request.user.trainees.group.id)

        context = {
            'title': 'Trainee - Assignment',
            'assignment_active': 'active',
            'assignments': assignmentData,
            'groupData': groupData,
            'assignments_total': assignmentData.count,
        }
        return render(request, 'main/trainee/assignmentList.html', context)

    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TraineeLogin)


@login_required(login_url='trainee_login')
def TraineeDashboard_traineeProfile(request, pk):
    if request.user.is_authenticated and request.user.is_trainee==True:
        group_member = pk
        # getting cohort
        if Trainee.objects.filter(id=group_member, stack=request.user.trainees.stack).exists():
            # get trainee as group member
            trainee = Trainee.objects.get(id=group_member, stack=request.user.trainees.stack)
            context = {
                'title': 'Trainer - Group member Profile',
                'trainees_active': 'active',
                'trainee': trainee,
            }
            return render(request, 'main/trainee/groupMember_profile.html', context)
        else:
            messages.error(request, ('Group member not found'))
            return redirect(TraineeDashboard_assignmentList)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TraineeLogin)


@login_required(login_url='trainee_login')
def TraineeDashboard_assignmentDetails(request, pk):
    if request.user.is_authenticated and request.user.is_trainee==True:
        assignment_id = pk
        if Assignment.objects.filter(stack=request.user.trainees.stack, id=assignment_id).exists():
            # if exists
            selectedAssignment = Assignment.objects.get(stack=request.user.trainees.stack, id=assignment_id)
            # getting group
            groupData = Group.objects.filter(id=request.user.trainees.group.id)
            # getting assignment reports
            if AssignmentReport.objects.filter(assignment=selectedAssignment, group=request.user.trainees.group.id).exists():
                reportData = AssignmentReport.objects.get(assignment=selectedAssignment, group=request.user.trainees.group.id)
            else:
                reportData=None

            if 'submit' in request.POST:
                # Retrieve the form data from the request
                description = request.POST.get('description')
                documentFiles =request.FILES.get('documentFiles')

                if description:
                    # create feedback
                    myGroup = Group.objects.get(id=request.user.trainees.group.id)
                    if documentFiles:
                        report = AssignmentReport(
                            assignment=selectedAssignment,
                            group =myGroup,
                            description =description,
                            documentFiles =documentFiles
                        )
                        report.save()
                    else:
                        report = AssignmentReport(
                            assignment=selectedAssignment,
                            group =myGroup,
                            description =description,
                        )
                        report.save()
                    messages.success(request, "Report submitted successfully.")
                    return redirect(TraineeDashboard_assignmentDetails, pk)
                else:
                    messages.error(request, "All fields are required.")
                    return redirect(TraineeDashboard_assignmentDetails, pk)

            elif 'update_report' in request.POST:
                # Retrieve the form data from the request
                description = request.POST.get('description')
                documentFiles = request.FILES.get('documentFiles')

                if description:
                    report = AssignmentReport.objects.get(assignment=selectedAssignment, group=request.user.trainees.group.id)
                    if documentFiles:
                        if report.documentFiles:
                            # check if existing module have document
                            if len(report.documentFiles) != 0:
                                report.documentFiles.delete()

                        # Update module with document file
                        updateReport = AssignmentReport.objects.filter(assignment=selectedAssignment, group=request.user.trainees.group.id).update(
                            description =description,
                            documentFiles=documentFiles
                        )
                    else:
                        # Update Report
                        updateReport = AssignmentReport.objects.filter(assignment=selectedAssignment, group=request.user.trainees.group.id).update(
                            description =description,
                        )

                    if updateReport:
                        messages.success(request, "Report submitted successfully.")
                        return redirect(TraineeDashboard_assignmentDetails, pk)
                else:
                    messages.error(request, "All fields are required.")
                    return redirect(TraineeDashboard_assignmentDetails, pk)

            else:
                canSubmit=False
                if selectedAssignment.startDate < timezone.now() and selectedAssignment.dueDate > timezone.now():
                    canSubmit=True
                else:
                    canSubmit=False
                context = {
                    'title': 'Trainee - Assignment Info',
                    'assignment_active': 'active',
                    'assignment': selectedAssignment,
                    'groupData': groupData,
                    'report': reportData,
                    'canSubmit': canSubmit
                }
                return render(request, 'main/trainee/assignmentDetails.html', context)
        else:
            messages.error(request, ('Assignment not found'))
            return redirect(TraineeDashboard_assignmentList)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TraineeLogin)