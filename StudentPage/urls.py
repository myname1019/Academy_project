from django.urls import path
from . import views

app_name = 'StudentPage'
urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
]