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

    # 강의 가격 (음수 방지: 양수만 허용)
    price = models.PositiveIntegerField()

    # 강의 카테고리 (MainPage 브랜치 내용)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='etc'
    )

    # 강의 썸네일 (teacher-dashboard 브랜치 내용)
    thumbnail = models.ImageField(
        upload_to="course_thumbnails/",
        blank=True,
        null=True,
    )

    # 동영상 파일 필드
    video = models.FileField(upload_to="videos/%Y/%m/%d/", blank=True, null=True)

    # 강사(선생님)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_courses",
        null=True,
        blank=True,
    )

    # 수강생들 (ManyToMany)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="student_courses",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # [수정] 최신순 정렬 추가
        ordering = ['-created_at']

    def __str__(self):
        return self.title