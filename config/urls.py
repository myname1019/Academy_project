# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from Main import views  # 메인 페이지 뷰 사용(팀원 구조 유지)

urlpatterns = [
    # 관리자
    path("admin/", admin.site.urls),

    # 메인
    path("", views.main_page, name="main_page"),

    # 게시판
    path("Board/", include("Board.urls")),

    # 공통(로그인/로그아웃/회원가입 등)
    path("common/", include("common.urls")),

    # 강의 앱
    # course/urls.py 안에 app_name = "course"가 있다면 namespace 지정은 보통 불필요합니다.
    path("course/", include("course.urls")),

    # 학생 페이지
    path("StudentPage/", include("StudentPage.urls")),

    # 강사 페이지 (현재 너가 쓰던 경로: /teacher/)
    path("teacher/", include("TeacherPage.urls")),

    # 리뷰 앱이 실제로 설치돼 있고 urls.py가 존재할 때만 사용
    path("review/", include("review.urls")),
]

# 개발환경에서만 MEDIA 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)