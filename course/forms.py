from django import forms
from .models import Course


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'category', 'thumbnail', 'video']  # ✅ thumbnail 추가

        labels = {
            'title': '강의 제목',
            'description': '강의 설명',
            'price': '수강료',
            'category': '카테고리',
            'thumbnail': '강의 썸네일',  
            'video': '강의 영상',
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '강의 제목을 입력하세요'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': '강의 설명을 입력하세요'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '수강료 입력'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'thumbnail': forms.ClearableFileInput(attrs={ 
                'class': 'form-control'
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('수강료는 0원 이상이어야 합니다.')
        return price