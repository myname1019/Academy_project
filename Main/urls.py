from django.urls import path
from . import views

app_name = 'Main'
urlpatterns = [
    path('', views.main_page, name='main_page'),
    # 💡 검색 페이지 URL 추가
    path('search/', views.search_page, name='search_page'),
]