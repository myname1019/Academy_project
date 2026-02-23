from django.db import models
from django.conf import settings
from django.db.models import Avg, Count

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
# 강의 가격 (음수 방지: 양수만 허용)
    price = models.PositiveIntegerField()

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

    # 수강생들
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="student_courses",
        blank=True,
    )

    # 강의 썸네일
    thumbnail = models.ImageField(
        upload_to="course_thumbnails/",
        blank=True,
        null=True,
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_courses',
        null=True,
        blank=True
    )

    # 수강생들 (ManyToMany)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='student_courses',
        blank=True
    )

    #추가할 썸네일 필드 (반드시 Course 안에 있어야 함!)
    thumbnail = models.ImageField(
        upload_to="course_thumbnails/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

    def get_average_rating(self):
        avg = self.reviews.aggregate(
            Avg('rating')
        )['rating__avg']
        return round(avg, 1) if avg else 0
    
    def get_rating_distribution(self):
        distribution = {i: 0 for i in range(1, 6)}
        qs = self.reviews.values('rating').annotate(
            count=Count('rating')
        )
        for item in qs:
            distribution[item['rating']] = item['count']
        return distribution
    
    def get_review_count(self):
        return self.reviews.count()