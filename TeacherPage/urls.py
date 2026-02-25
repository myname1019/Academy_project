# TeacherPage/urls.py
from django.urls import path
from . import views

app_name = "teacherpage"

urlpatterns = [
    path("", views.teacher_dashboard, name="dashboard"),
    path("course/create/", views.create_course, name="course_create"),
    path("course/<int:course_id>/edit/", views.edit_course, name="course_edit"),
    path("course/<int:course_id>/delete/", views.delete_course, name="course_delete"),
    path("course/<int:course_id>/students/", views.course_students, name="course_students"),
]