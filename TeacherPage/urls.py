from django.urls import path
from . import views

app_name = 'TeacherPage'

urlpatterns = [
    path('', views.teacher_dashboard, name='teacher_dashboard'),  # 이름 맞춤
]