from django.contrib import admin
from django.urls import path, include
from Main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('Board/', include('Board.urls')),
    path('', views.Main),
    path('common/', include('common.urls')),
    
    # 1. main 브랜치의 namespace 설정을 채택합니다.
    path('course/', include('course.urls', namespace='course')),
    
    # 2. StudentPage 연결 (feature 브랜치)
    path('StudentPage/', include('StudentPage.urls')),
    
    # 3. TeacherPage 연결 (test 브랜치 버전 살림 + namespace 추가 권장)
    # 만약 TeacherPage/urls.py 안에 app_name이 설정되어 있다면 namespace를 빼셔도 됩니다.
    path('TeacherPage/', include('TeacherPage.urls', namespace='TeacherPage')),
    path('review/', include('review.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

