from django.urls import path
from . import views

app_name = 'studentpage'
urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('checkout/<int:course_id>/', views.course_checkout, name='course_checkout'),
]