
from datetime import date
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash

from account.models import Trainer, Trainee, ProgramManager, Company
from .models import Stack, Cohort, Module
from recruitment.models import Application

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
                    more = more,
                    status = "Pending"
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
        # getting stacks
        StacksData = Stack.objects.filter()
        # getting trainers
        TrainersData = Trainer.objects.filter()
        # getting cohort
        CohortData = Cohort.objects.filter()
        context = {
            'title': 'Manager Dashboard', 
            'dash_active': 'active', 
            'cohorts': CohortData,
            'stack_total': StacksData.count(),
            'trainer_total': TrainersData.count(),
            'team': TrainersData,
        }
        return render(request, 'main/manager/dashboard.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(ManagerLogin)


@login_required(login_url='manager_login')
def Manager_profile(request):
    if request.user.is_authenticated and request.user.is_manager==True:
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
            locationAddress = request.POST.get('locationAddress')
            profilePicture = request.FILES.get('profilePicture')

            if first_name and last_name and email and gender and phone1 and phone2 and specialization and ssn and locationAddress and profilePicture:
                if get_user_model().objects.filter(email=email):
                    messages.warning(request, "Email already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(ssn=ssn):
                    messages.warning(request, "SSN already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(phone1=phone1):
                    messages.warning(request, "Phone 1 already exist.")
                    return redirect(ManagerDashboard_team)
                else:
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
            # getting cohort
            CohortData = Cohort.objects.filter()

            context = {
                'title': 'Manager - Team',
                'team': teamData,
                'team_total': teamData.count,
                'team_active': 'active',
                'cohorts': CohortData,
            }
            return render(request, 'main/manager/team.html', context)
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
                ssn = request.POST.get('ssn')
                locationAddress = request.POST.get('locationAddress')
                profilePicture = request.FILES.get('profilePicture')

                if first_name and last_name and email and gender and phone1 and phone2 and specialization and ssn and locationAddress:
                    if get_user_model().objects.filter(email=email).exclude(id=foundData.user.id):
                        messages.warning(request, "Email already exist.")
                        return redirect(ManagerDashboard_team)
                    elif Trainer.objects.filter(ssn=ssn).exclude(id=trainer_id):
                        messages.warning(request, "SSN already exist.")
                        return redirect(ManagerDashboard_team)
                    elif Trainer.objects.filter(phone1=phone1).exclude(id=trainer_id):
                        messages.warning(request, "Phone 1 already exist.")
                        return redirect(ManagerDashboard_team)
                    else:
                        # Update Trainer account
                        user =  get_user_model().objects.filter(id=foundData.user.id).update(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            gender=gender,
                        )
                        if user:
                            if len(profilePicture) > 0:
                                data = Trainer.objects.get(id=trainer_id)
                                if len(data.profilePicture) > 0:
                                    data.profilePicture.delete()

                                # Update trainer profile
                                data.ssn = ssn
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
                                    phone1=phone1,
                                    phone2=phone2,
                                    specialization=specialization,
                                    locationAddress=locationAddress,
                                )

                            if updateTrainer:
                                messages.success(request, "Trainer "+first_name+", Updated successfully.")
                                return redirect(ManagerDashboard_team)
                            else:
                                messages.error(request, ('Process Failed.'))
                                return redirect(ManagerDashboard_team)
                        else:
                            messages.error(request, ('Process Failed.'))
                            return redirect(ManagerDashboard_team)
                else:
                    messages.error(request, ('All fields are required.'))
                    return redirect(ManagerDashboard_teamEdit)

            elif 'delete' in request.POST:
                # Delete Trainer
                delete_trainer = get_user_model().objects.get(id=foundData.user.id)
                delete_trainer.delete()
                messages.success(request, "Trainer info deleted successfully.")
                return redirect(ManagerDashboard_team)

            else:
                # getting cohort
                CohortData = Cohort.objects.filter()
                context = {
                    'title': 'Manager - Trainer Info',
                    'team_active': 'active',
                    'profile_data': trainerData,
                    'cohorts': CohortData,
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
        TraineesData = Trainee.objects.filter(cohort=currCohort)
        # getting Modules
        ModulesData = Module.objects.filter()
        # getting cohort
        CohortData = Cohort.objects.filter()
        context = {
            'title': 'Trainer Dashboard', 
            'dash_active': 'active', 
            'cohorts': CohortData,
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
def TrainerDashboard_module(request):
    if request.user.is_authenticated and request.user.is_trainer==True:
        if request.method == 'POST':
            module_name = request.POST.get("module_name")
            description = request.POST.get("description")

            if module_name:
                # module_name=module_name.upper()
                found_data = Module.objects.filter(name=module_name)
                if found_data:
                    messages.warning(request, "Module "+module_name+", Already exist.")
                    return redirect(TrainerDashboard_module)
                else:
                    # add new stack
                    add_stack = Module(
                        name=module_name, 
                        description=description
                    )
                    add_stack.save()

                    messages.success(request, "New Module created successfully.")
                    return redirect(TrainerDashboard_module)
            else:
                messages.error(request, "Error , Module name is required!")
                return redirect(TrainerDashboard_module)
        else:
            # getting sodules
            ModuleData = Module.objects.filter()
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Trainer - Modules',
                'module_active': 'active', 
                'cohorts': CohortData,
                'modules': ModuleData,
                'module_total': ModuleData.count(),
            }
            return render(request, 'main/trainer/modules.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)




@login_required(login_url='trainer_login')
def TrainerDashboard_traineeList(request, pk):
    if request.user.is_authenticated and request.user.is_trainer==True:
        if request.method == 'POST':
            module_name = request.POST.get("module_name")
            description = request.POST.get("description")

            if module_name:
                # module_name=module_name.upper()
                found_data = Stack.objects.filter(name=module_name)
                if found_data:
                    messages.warning(request, "Stack "+module_name+", Already exist.")
                    return redirect(TrainerDashboard_module)
                else:
                    # add new stack
                    add_stack = Stack(
                        name=module_name, 
                        description=description
                    )
                    add_stack.save()

                    messages.success(request, "New Stack created successfully.")
                    return redirect(TrainerDashboard_module)
            else:
                messages.error(request, "Error , Stack name is required!")
                return redirect(TrainerDashboard_module)
        else:
            # getting stacks
            StackData = Stack.objects.filter()
            # getting cohort
            CohortData = Cohort.objects.filter()
            context = {
                'title': 'Trainer - Courses',
                'course_active': 'active', 
                'cohorts': CohortData,
                'courses': StackData,
                'course_total': StackData.count(),
            }
            return render(request, 'main/trainer/trainee_list.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)



@login_required(login_url='trainer_login')
def TrainerDashboard_assignmentList(request, pk):
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
            locationAddress = request.POST.get('locationAddress')
            profilePicture = request.FILES.get('profilePicture')

            if first_name and last_name and email and gender and phone1 and phone2 and specialization and ssn and locationAddress and profilePicture:
                if get_user_model().objects.filter(email=email):
                    messages.warning(request, "Email already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(ssn=ssn):
                    messages.warning(request, "SSN already exist.")
                    return redirect(ManagerDashboard_team)
                elif Trainer.objects.filter(phone1=phone1):
                    messages.warning(request, "Phone 1 already exist.")
                    return redirect(ManagerDashboard_team)
                else:
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
                            ssn=ssn,
                            profilePicture=profilePicture,
                            phone1=phone1,
                            phone2=phone2,
                            specialization=specialization,
                            locationAddress=locationAddress,
                        )
                        trainerProfile.save()
                        messages.success(request, "Trainer "+first_name+", created successfully.")
                        return redirect(TrainerDashboard_assignmentList)
                    else:
                        messages.error(request, ('Process Failed.'))
                        return redirect(TrainerDashboard_assignmentList)
            else:
                messages.error(request, ('All fields are required.'))
                return redirect(TrainerDashboard_assignmentList)
        else:
            # getting team
            teamData = Trainer.objects.filter()
            # getting cohort
            CohortData = Cohort.objects.filter()

            context = {
                'title': 'Manager - Team',
                'team': teamData,
                'team_total': teamData.count,
                'team_active': 'active',
                'cohorts': CohortData,
            }
            return render(request, 'main/trainer/assignmentList.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(TrainerLogin)
