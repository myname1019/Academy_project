from django import forms
from .models import Course, Lesson  # ✅ Lesson 모델 추가 임포트

# 1. 강의 기본 정보를 입력받는 폼
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        # 💡 이제 영상은 Lesson에서 관리하므로 'video' 필드는 제외해도 됩니다. 
        # 만약 '소개 영상' 용도로 남겨두고 싶다면 그대로 두셔도 무방합니다.
        fields = ['title', 'description', 'price', 'category', 'thumbnail']

        labels = {
            'title': '강의 제목',
            'description': '강의 설명',
            'price': '수강료',
            'category': '카테고리',
            'thumbnail': '강의 썸네일',
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '강의 제목을 입력하세요'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '강의 설명을 입력하세요'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '수강료 입력'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('수강료는 0원 이상이어야 합니다.')
        return price


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video', 'order']
        labels = {
            'title': '영상 제목 (예: 1강. OT)',
            'video': '강의 영상 파일',
            'order': '재생 순서',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'value': 1}),
        }