from django.contrib.auth.models import AbstractUser
from django.db import models

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