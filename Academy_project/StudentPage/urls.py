from django.urls import path
from . import views

app_name = 'studentpage'  # 네임스페이스 지정 (선택)

urlpatterns = [
    path('', views.home, name='home'),  # /student/ 접속 시
]
