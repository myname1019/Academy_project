from django import forms
from .models import Course

class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        # 모든 필드(제목, 설명, 가격, 비디오)를 포함합니다.
        fields = ['title', 'description', 'price', 'video']

        labels = {
            'title': '강의 제목',
            'description': '강의 설명',
            'price': '수강료',
            'video': '강의 영상',
        }

        # 깔끔한 부트스트랩 디자인(form-control)과 placeholder를 모두 합칩니다.
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
            # main 브랜치의 동영상 업로드 위젯 설정을 유지합니다.
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    # 추가 유효성 검사 (수강료가 마이너스가 되지 않도록 방지)
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('수강료는 0원 이상이어야 합니다.')
        return price