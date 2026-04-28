from django.db import models
from django.conf import settings  # ✅ 유저 모델을 가져오기 위해 필요합니다.

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('notice', '공지사항'),
        ('community', '게시판'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # ✅ 기존 CharField를 삭제하고 ForeignKey로 변경합니다.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"