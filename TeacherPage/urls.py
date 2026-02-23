<<<<<<< HEAD
# TeacherPage/urls.py

from django.urls import path
from . import views

app_name = "teacherpage"

urlpatterns = [
    path("", views.teacher_dashboard, name="dashboard"),
    path("course/create/", views.create_course, name="course_create"),
    path("course/<int:course_id>/edit/", views.edit_course, name="course_edit"),
    path("course/<int:course_id>/delete/", views.delete_course, name="course_delete"),
=======
from django.urls import path
from . import views

app_name = 'TeacherPage'

urlpatterns = [
    path('', views.teacher_dashboard, name='teacher_dashboard'),  # 이름 맞춤
>>>>>>> main
]