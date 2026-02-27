from django.urls import path
from . import views

app_name='Board'

urlpatterns=[
    # ==========================================
    # 0. 메인 화면
    # ==========================================
    path('', views.board_list, name='list'),

    # ==========================================
    # 1. 공지사항 관련 주소 (Notice)
    # ==========================================
    path('notice/', views.notice_list, name='notice_list'),
    path('notice/create/', views.notice_create, name='notice_create'),
    path('notice/<int:post_id>/', views.notice_detail, name='notice_detail'),
    path('notice/edit/<int:post_id>/', views.notice_edit, name='notice_edit'), #공지사항 수정 주소
    path('notice/delete/<int:post_id>/', views.notice_delete, name='notice_delete'), #공지사항 삭제 주소

    # ==========================================
    # 2. 자유게시판 관련 주소 (Community)
    # ==========================================
    path('community/', views.community_list, name='community_list'),
    path('community/create/', views.community_create, name='community_create'),
    path('community/<int:post_id>/', views.community_detail, name='community_detail'), 
    path('community/edit/<int:post_id>/', views.community_edit, name='community_edit'), #특정 글의 수정 페이지로 가기 위한
    path('community/delete/<int:post_id>/', views.community_delete, name='community_delete'), # 게시판글 삭제 코드
]