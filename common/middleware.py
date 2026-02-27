from django.shortcuts import redirect
from django.urls import reverse

class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            # 허용할 URL들 (로그아웃, 역할선택, 관리자 등)
            allowed_paths = [
                reverse('common:social_signup_role'),
                reverse('common:logout'),
            ]

            if not request.user.role and request.path not in allowed_paths:
                return redirect('common:social_signup_role')

        return self.get_response(request)