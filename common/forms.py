# forms.py
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model # 기본 User 대신 우리가 세팅한 모델을 불러오는 안전한 방법

User = get_user_model()

class UserForm(UserCreationForm):
    class Meta:
        model = User
        # 비밀번호 1, 2는 UserCreationForm이 알아서 만들어주므로 적지 않아도 됩니다!
        # 새로 만든 role 필드를 추가해 줍니다.
        fields = ("username", "email", "role")
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # 만약 입력한 이메일과 똑같은 이메일을 가진 유저가 존재한다면?
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 가입된 이메일입니다. 다른 이메일을 사용해 주세요.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # 영문 대소문자, 숫자, 언더바(_), 하이픈(-)만 허용하는 규칙
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError("아이디는 영문, 숫자, 언더바(_), 하이픈(-)만 사용할 수 있습니다.")
            
        return username
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "email", "profile_image", "bio")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # 자기 자신은 제외하고 검사
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")

        return email