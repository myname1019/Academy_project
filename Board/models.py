from django.db import migrations, models

class Post(models.Model):
    # 'notice' 또는 'community'로 구분
    CATEGORY_CHOICES = [
        ('notice', '공지사항'),
        ('community', '게시판'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"