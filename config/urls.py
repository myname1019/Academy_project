from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from Main import views  # 메인 페이지 뷰 사용

urlpatterns = [
    # 관리자
    path("admin/", admin.site.urls),

    # 메인 (수정했던 main_page 함수 사용)
    
    path("",include("Main.urls")),

    # 게시판
    path("Board/", include("Board.urls")),

    # 공통(로그인/로그아웃/회원가입 등)
    path("common/", include("common.urls")),

    # 강의 앱 (각 앱의 urls.py 안에 app_name이 있으므로 namespace 생략)
    path("course/", include("course.urls")),

    # 학생 페이지
    path("studentpage/", include("StudentPage.urls")),

    # 강사 페이지 (URL 주소는 소문자 'teacher/'로 깔끔하게 통일)
    path("teacher/", include("TeacherPage.urls")),

    # 리뷰 앱
    path("review/", include("review.urls")),
    
    # 1:1 채팅 앱
    path("chat/", include("chat.urls")),

    # 소셜 로그인
    path('accounts/', include('allauth.urls')),
]

# 개발환경(DEBUG=True)에서만 미디어 파일 서빙 (안전한 방식)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)