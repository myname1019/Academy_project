from django.urls import path
from . import views

urlpatterns = [
    # 클래스형 뷰는 반드시 뒤에 .as_view() 를 붙여야 합니다!
    path('', views.MainPageView.as_view(), name='main_page'),
    path('search/', views.SearchPageView.as_view(), name='search_page'),
]