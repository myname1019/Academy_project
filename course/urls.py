from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('', views.CourseList.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetail.as_view(), name='course_detail'),
    
    # 💡 템플릿과 짝을 맞추기 위해 <int:pk>가 없는 main 브랜치 코드를 채택합니다!
    path('create/', views.CourseCreate.as_view(), name='course_create'),
    
    path('<int:pk>/update/', views.CourseUpdate.as_view(), name='course_update'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
]