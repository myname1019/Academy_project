from django.urls import path

from . import views

app_name = 'course'

urlpatterns = [
    path('', views.CourseList.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetail.as_view(), name='course_detail'),
    path('create/', views.CourseCreate.as_view(), name='course_create'),
    path('<int:pk>/update/', views.CourseUpdate.as_view(), name='course_update'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
]