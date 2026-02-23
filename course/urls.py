from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('', views.CourseList.as_view(), name='course_list'),
    path('<int:pk>/', views.CourseDetail.as_view(), name='course_detail'),
    
    # 💡 강의 생성 시에는 아직 번호(pk)가 없으므로 main 브랜치 설정을 유지합니다.
    path('create/', views.CourseCreate.as_view(), name='course_create'),
    
    path('<int:pk>/update/', views.CourseUpdate.as_view(), name='course_update'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
]