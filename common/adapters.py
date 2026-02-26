from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from .models import Student, Teacher

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    # 1️⃣ [중요] 회원가입 시 'role'이 비어있어서 에러나는 것을 방지
    def save_user(self, request, sociallogin, form=None):
        # 부모 클래스의 기본 저장 기능을 먼저 수행 (유저 생성)
        user = super().save_user(request, sociallogin, form)
        
        # 유저에게 임시로 'none' 또는 빈 문자열 역할 부여 (DB 에러 방지용!)
        # (나중에 역할 선택 페이지에서 제대로 된 역할로 바뀔 것입니다)
        if not user.role:
            user.role = 'none' 
            user.save()
        
        return user

    # 2️⃣ [회원님 코드] 로그인 후 이동할 주소 결정
    def get_login_redirect_url(self, request):
        user = request.user
        
        # DB 조회 (프로필 존재 여부 확인)
        # getattr를 쓰면 에러 없이 안전하게 가져올 수 있습니다.
        is_student = Student.objects.filter(user=user).exists()
        is_teacher = Teacher.objects.filter(user=user).exists()
        
        # 프로필이 둘 다 없으면 "무조건" 역할 선택 페이지로 보냄
        if not is_student and not is_teacher:
            # 아직 역할 선택 페이지 URL을 안 만드셨다면 임시로 메인('/')으로 가도록 해도 됩니다.
            # 지금은 에러 방지를 위해 role 선택 페이지가 있다고 가정합니다.
            return resolve_url('common:social_signup_role')
            
        # 역할이 있다면 각각의 페이지로 이동
        if user.role == 'student':
            return resolve_url('/StudentPage/') # URL 패턴 이름이 있다면 그걸 쓰는 게 더 좋습니다
        elif user.role == 'teacher':
            return resolve_url('/TeacherPage/dashboard/')
            
        return resolve_url('/')