from django.urls import path
from . import views

app_name='Board'
urlpatterns=[
  path('', views.board_list,name='list'),
  path('notice/', views.notice_list, name='notice_list'),
  path('community/', views.community_list, name='community_list'),
]
