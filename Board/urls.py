from django.urls import path
from . import views

app_name='Board'
urlpatterns=[
  path('', views.board_list,name='list'), # 127.0.0.1/MTV 를 찍고 들어와야 매치가 된다.
]