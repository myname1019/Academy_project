from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# 1. 공통 로그인 테이블 (출입문)
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', '학생'),
        ('teacher', '선생님'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name="가입 유형")
    bio = models.TextField(blank=True, null=True, verbose_name="자기소개")

    # ✅ 추가
    profile_image = models.ImageField(upload_to="profile/", blank=True, null=True, verbose_name="프로필 이미지")
    last_password_change = models.DateTimeField(auto_now_add=True, verbose_name="마지막 비밀번호 변경일")

    # 💡 2. 90일이 지났는지 계산해주는 똑똑한 속성 (HTML에서 바로 쓸 수 있어요!)
    @property
    def is_password_expired(self):
        # 마지막 변경일 + 90일이 지금 시간보다 과거라면? -> 만료된 것!
        expiration_date = self.last_password_change + timedelta(days=90) # 💡 테스트용으로 0초로 설정 (실제론 90일 = 90*24*60*60 초)
        return timezone.now() >= expiration_date
# 2. 학생 전용 테이블 따로 만들기
class Student(models.Model):
    # CustomUser 테이블과 1:1로 연결! (유저가 삭제되면 학생 정보도 같이 삭제됨)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    
    # 학생만의 추가 정보 예시 (원하시는 대로 자유롭게 추가하세요!)
    grade = models.IntegerField(default=1, verbose_name="학년")
    
    def __str__(self):
        return f"{self.user.username} (학생)"

# 3. 선생님 전용 테이블 따로 만들기
class Teacher(models.Model):
    # CustomUser 테이블과 1:1로 연결!
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    
    # 선생님만의 추가 정보 예시
    subject = models.CharField(max_length=50, blank=True, verbose_name="담당 과목")
    
    def __str__(self):
        return f"{self.user.username} (선생님)"

class PasswordHistory(models.Model):
    # 어떤 유저의 비밀번호 기록인지 연결
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_histories')
    # 암호화된 비밀번호 저장 (장고의 해시값은 보통 128자를 넘지 않습니다)
    password_hash = models.CharField(max_length=128)
    # 언제 변경했던 비밀번호인지 기록
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # 최신 변경일 순으로 정렬

    def __str__(self):
        return f"{self.user.username}님의 비밀번호 변경 기록 ({self.created_at.strftime('%Y-%m-%d')})"
    
