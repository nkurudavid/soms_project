from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePage, name='home_page'),
    path('join_us/apply', ApplicationPage, name='join_page'),

    # manager urls
    path('staff/manager/login', ManagerLogin, name='manager_login'),
    path('staff/manager/logout', ManagerLogout, name='manager_logout'),
    path('staff/manager/dashboard', ManagerDashboard, name='manager_dashboard'),
    path('staff/manager/dashboard/my_profile', Manager_profile, name='manager_profile'),
    path('staff/manager/dashboard/our_team', ManagerDashboard_team, name='manager_team'),
    path('staff/manager/dashboard/our_team/<int:pk>/trainer_info', ManagerDashboard_teamEdit, name='manager_trainerEdit'),
    path('staff/manager/dashboard/stacks', ManagerDashboard_stacks, name='manager_stacks'),
    path('staff/manager/dashboard/stacks/<int:pk>/stack_info', ManagerDashboard_stackEdit, name='manager_stackEdit'),
    path('staff/manager/dashboard/cohorts', ManagerDashboard_cohorts, name='manager_cohorts'),
    path('staff/manager/dashboard/cohorts/<int:pk>/cohort_info', ManagerDashboard_cohortEdit, name='manager_cohortEdit'),
    path('staff/manager/dashboard/cohorts/<int:pk>/application_list', ManagerDashboard_applicationList, name='manager_applicantsList'),
    path('staff/manager/dashboard/cohorts/<int:pk>/application_list/<int:n>/application_details', ManagerDashboard_applicationDetails, name='manager_applicationDetails'),
    path('staff/manager/dashboard/cohorts/<int:pk>/trainees_list', ManagerDashboard_traineesList, name='manager_traineesList'),
    path('staff/manager/dashboard/cohorts/<int:pk>/trainees_list/<int:n>/trainee_profile', ManagerDashboard_traineeProfile, name='manager_traineesProfile'),

    # Trainer urls
    path('staff/trainer/login', TrainerLogin, name='trainer_login'),
    path('staff/trainer/logout', TrainerLogout, name='trainer_logout'),
    path('staff/trainer/dashboard', TrainerDashboard, name='trainer_dashboard'),
    path('staff/trainer/dashboard/my_profile', Trainer_profile, name='trainer_profile'),
    path('staff/trainer/dashboard/modules', TrainerDashboard_module, name='trainer_modules'),
    path('staff/trainer/dashboard/modules/<int:pk>/module_info', TrainerDashboard_moduleEdit, name='trainer_moduleEdit'),
    path('staff/trainer/dashboard/cohorts/<int:pk>/trainees', TrainerDashboard_traineeList, name='trainer_traineeList'),
    path('staff/trainer/dashboard/cohorts/<int:pk>/trainees_list/<int:n>/trainee_profile', TrainerDashboard_traineeProfile, name='trainer_traineeProfile'),
    path('staff/trainer/dashboard/cohorts/<int:pk>/assignments', TrainerDashboard_assignmentList, name='trainer_assignmentList'),
    path('staff/trainer/dashboard/cohorts/<int:pk>/assignments/<int:n>/assignment', TrainerDashboard_assignmentEdit, name='trainer_assignmentDetails'),
    path('staff/trainer/dashboard/cohorts/<int:pk>/assignments/<int:n>/assignment/<int:k>/report', TrainerDashboard_reportCollection, name='trainer_assignmentReport'),

]
