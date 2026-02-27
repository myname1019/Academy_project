from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def get_login_redirect_url(self, request):
        user = request.user

        # ✅ role이 없으면 역할 선택 페이지로
        if not user.role:
            return resolve_url('common:social_signup_role')

        # ✅ 이미 역할이 있으면 메인으로
        return resolve_url('/')