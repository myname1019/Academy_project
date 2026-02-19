# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 선택지 만들기: 왼쪽은 DB에 저장될 실제 값, 오른쪽은 화면에 보일 이름
    ROLE_CHOICES = (
        ('student', '학생'),
        ('teacher', '선생님(지식공유자)'),
    )
    
    # role(역할) 필드 추가
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name="가입 유형")