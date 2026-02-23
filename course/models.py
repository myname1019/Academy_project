from django.db import models
from django.conf import settings

class Course(models.Model):

    CATEGORY_CHOICES = [
        ('korean', '국어'),
        ('math', '수학'),
        ('english', '영어'),
        ('social', '사회'),
        ('science', '과학'),
        ('etc', '기타'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    price = models.PositiveIntegerField()

    # 카테고리 필드 추가
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='etc'
    )

    video = models.FileField(upload_to='videos/%Y/%m/%d/', blank=True, null=True)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_courses',
        null=True,
        blank=True
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='student_courses',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title