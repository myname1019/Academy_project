# common/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from .models import CustomUser

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        """
        소셜 로그인 시 username을 user1, user2... 순서대로 자동 생성
        first_name, last_name은 구글에서 가져옴
        """
        user = super().populate_user(request, sociallogin, data)

        # 1️⃣ 이름 정보 가져오기
        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")

        # 2️⃣ username 자동 생성: user1, user2, user3 ...
        base_username = "user"
        counter = 1
        while True:
            username = f"{base_username}{counter}"
            if not CustomUser.objects.filter(username=username).exists():
                break
            counter += 1

        user.username = username

        return user

    def get_login_redirect_url(self, request):
        user = request.user

        # ✅ role이 없으면 역할 선택 페이지로
        if not user.role:
            return resolve_url('common:social_signup_role')

        # ✅ 이미 역할이 있으면 메인으로
        return resolve_url('/')