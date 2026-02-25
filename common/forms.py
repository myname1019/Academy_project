# forms.py
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model # 기본 User 대신 우리가 세팅한 모델을 불러오는 안전한 방법
from django.contrib.auth.forms import PasswordResetForm

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


class CustomPasswordResetForm(PasswordResetForm):
    # 💡 기존 이메일 칸에 더해서 '아이디' 입력 칸을 새로 추가합니다.
    username = forms.CharField(
        label="아이디",
        max_length=150,
    )

    # 💡 이메일을 보낼 유저를 찾는 핵심 함수를 가로채서 수정합니다!
    def get_users(self, email):
        # 1. 일단 원래 장고 방식대로 이메일이 일치하는 유저들을 가져옵니다.
        active_users = super().get_users(email)
        
        # 2. 사용자가 화면에 입력한 아이디(username)를 가져옵니다.
        input_username = self.cleaned_data.get('username')
        
        # 3. 이메일도 맞고, 아이디도 똑같은 유저만 걸러서(필터링) 돌려줍니다!
        # 만약 아이디가 다르면 아무에게도 메일을 보내지 않게 됩니다.
        return (user for user in active_users if user.username == input_username)