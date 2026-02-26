from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path("my/", views.my_reviews, name="my_reviews"),   # ✅ 추가
    path('create/<int:course_id>/', views.review_create, name='review_create'),
    path('update/<int:pk>/', views.review_update, name='review_update'),
    path('delete/<int:pk>/', views.review_delete, name='review_delete'),
]