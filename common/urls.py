from django.urls import path, reverse_lazy
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
    path(
        'password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='common/password_change.html',
            success_url=reverse_lazy('common:mypage')
        ),
        name='password_change'
    ),
    path('find_username/', views.find_username, name='find_username'),
    # 1. 이메일 입력 화면
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='common/password_reset.html',
        email_template_name='common/password_reset_email.html',
        success_url=reverse_lazy('common:password_reset_done')  # 👈 💡 메일 보내고 갈 곳 지정!
    ), name='password_reset'),
    
    # 2. 이메일 전송 완료 안내 화면
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='common/password_reset_done.html'
    ), name='password_reset_done'),
    
    # 3. 새 비밀번호 입력 화면
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='common/password_reset_confirm.html',
        success_url=reverse_lazy('common:password_reset_complete')  # 👈 💡 비번 바꾸고 갈 곳 지정!
    ), name='password_reset_confirm'),
    
    # 4. 새 비밀번호 설정 완료 안내 화면
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='common/password_reset_complete.html'
    ), name='password_reset_complete'),
]