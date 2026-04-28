# TeacherPage/forms.py

from django import forms
from course.models import Course

class TeacherCourseForm(forms.ModelForm):
    """
    강사용 강의 생성/수정 폼
    - teacher는 views에서 자동 주입하므로 폼에 포함하지 않음
    - 썸네일(thumbnail) 업로드 포함
    """
    class Meta:
        model = Course
        fields = ("title", "description", "thumbnail", "video", "price")  # 필요하면 video 같은 필드도 추가