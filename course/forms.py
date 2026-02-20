from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'video']
        labels = {
            'title': '강의 제목',
            'description': '강의 설명',
            'price': '수강료',
            'video': '강의 동영상',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '강의 제목'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'placeholder': '강의 설명'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '수강료'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError('수강료는 0원 이상이어야 합니다.')
        return price