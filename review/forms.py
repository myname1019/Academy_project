from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'placeholder': '1~5점'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '리뷰 내용을 작성하세요'
            }),
        }

    # ✅ 공백만 입력 방지
    def clean_content(self):
        content = self.cleaned_data.get('content')

        if not content or not content.strip():
            raise forms.ValidationError("리뷰 내용을 입력해주세요.")

        return content.strip()