from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from .models import Student, Teacher

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        
        # Student나 Teacher 테이블에 이 유저의 PK가 들어있는지 확인
        is_student = Student.objects.filter(user=user).exists()
        is_teacher = Teacher.objects.filter(user=user).exists()
        
        if is_student or is_teacher:
            # 역할 정보가 이미 DB(프로필 테이블)에 있다면 메인 페이지로!
            return resolve_url('/') 
        else:
            # 역할 정보가 없다면 우리가 만든 역할 선택 뷰로!
            return resolve_url('common:social_signup_role')