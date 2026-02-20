from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # course2 브랜치의 더 안전한 필드(양수만 허용)를 선택합니다.
    price = models.PositiveIntegerField()
    
    # 동영상 파일 필드
    video = models.FileField(upload_to='videos/%Y/%m/%d/', blank=True, null=True)

    # feature/student-page(main 병합본)에서 추가한 선생님/학생 관계 필드를 유지합니다.
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_courses',
        null=True,      # 🔥 추가
        blank=True      # 🔥 추가
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='student_courses',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title