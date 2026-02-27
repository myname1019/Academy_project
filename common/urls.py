from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from common import views 

# 💡 에러 방지: forms.py에서 우리가 만든 커스텀 폼들을 꼭 가져와야 합니다!
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.urls import path, include


app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'), # 로그인 페이지 연결
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # 로그아웃 페이지 연결 (로그아웃 후 리다이렉트는 settings.py에서 LOGOUT_REDIRECT_URL로 설정)
    path('signup/', views.signup, name='signup'), # 회원가입 페이지 연결
    path('mypage/', views.mypage_redirect, name='mypage'), # 마이페이지로 연결 (로그인한 유저의 역할에 따라 학생/선생님 페이지로 리다이렉트)
    path("profile/edit/", views.profile_edit, name="profile_edit"), # 프로필 수정 페이지 연결
    path("profile/<str:username>/", views.profile_view, name="profile"), # 프로필 페이지 연결 (username을 URL에서 받아서 해당 유저의 프로필 보여줌)
    path("delete/", views.delete_account, name="delete_account"), # 회원 탈퇴 페이지 연결
    path( # 비밀번호 변경 페이지 연결 (로그인한 상태에서만 접근 가능)
        'password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='common/password_change.html',
            success_url=reverse_lazy('common:mypage')
        ),
        name='password_change'
    ),
    
    # ===== 여기서부터 another 브랜치의 최신 기능들입니다 =====
    
    path('find_username/', views.find_username, name='find_username'), # 아이디 찾기 페이지 연결
    
    # 1. 이메일 입력 화면
    path('password_reset/', auth_views.PasswordResetView.as_view( # 비밀번호 초기화 페이지 연결 (로그인하지 않은 상태에서 접근)
        template_name='common/password_reset.html',
        email_template_name='common/password_reset_email.html',
        success_url=reverse_lazy('common:password_reset_done'),  # 👈 💡 메일 보내고 갈 곳 지정!
        form_class=CustomPasswordResetForm
    ), name='password_reset'),
    
    # 2. 이메일 전송 완료 안내 화면
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view( 
        template_name='common/password_reset_done.html'
    ), name='password_reset_done'),
    
    # 3. 새 비밀번호 입력 화면
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='common/password_reset_confirm.html',
        success_url=reverse_lazy('common:password_reset_complete'),  # 👈 💡 비번 바꾸고 갈 곳 지정!
        form_class=CustomSetPasswordForm
    ), name='password_reset_confirm'),
    
    # 4. 새 비밀번호 설정 완료 안내 화면
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='common/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('accounts/', include('allauth.urls')),  # 소셜 로그인 URL 포함

    path('social-signup-role/', views.social_signup_role, name='social_signup_role'),


]