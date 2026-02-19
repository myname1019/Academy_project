from django.urls import path
from Board import views

app_name='course'
urlpatterns = [
    path('<int:pk>/', views.BoardDetail.as_view(), name='detail'),
    path('<int:pk>/list', views.BoardCreate.as_view(),name='board_create'),
    path('create_course', views.BoardDelete,name='board_delete'),
    path('update_course/<int:pk>', views.BoardUpdate.as_view(),name='board_update'),
    path('delete_course/<int:pk>', views.Board.as_view(),name='board_update'),
]