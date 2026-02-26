from django.urls import path
from . import views

app_name='Board'
urlpatterns=[
  path('', views.board_list,name='list'),
  path('notice/', views.notice_list, name='notice_list'),
  path('community/', views.community_list, name='community_list'),
  path('community/create/', views.community_create, name='community_create'),
  path('notice/create/', views.notice_create, name='notice_create'),
  path('notice/<int:post_id>/', views.notice_detail, name='notice_detail'),
  path('community/<int:post_id>/', views.community_detail, name='community_detail'), # 이 줄 추가!
  
]
