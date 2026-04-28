#chat/models.py
from django.conf import settings
from django.db import models
from course.models import Course

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    # 강의 기준으로 강사-학생 1:1 대화방을 만들기 위한 모델
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="conversations")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_conversations")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 같은 강의에서 같은 강사-학생 조합은 대화방 1개만 존재하도록 제한
        constraints = [
            models.UniqueConstraint(fields=["course", "teacher", "student"], name="uniq_course_teacher_student")
        ]

    def __str__(self):
        return f"{self.course_id} | {self.teacher_id} <-> {self.student_id}"


class Message(models.Model):
    # 특정 대화방에서 오가는 메시지
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 읽음 처리용 필드 추가
    is_read = models.BooleanField(default=False)  # 주석: 상대방이 읽었는지 여부
    read_at = models.DateTimeField(null=True, blank=True)  # 주석: 읽은 시간
    
    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender_id}: {self.content[:20]}"