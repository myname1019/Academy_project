from django.urls import path
from django.contrib.auth import views as auth_views
from common import views 

app_name = 'common'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('mypage/', views.mypage_redirect, name='mypage'),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("delete/", views.delete_account, name="delete_account"),
]