# forms.py
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model # 기본 User 대신 우리가 세팅한 모델을 불러오는 안전한 방법
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password # 💡 암호화된 비밀번호 비교용 함수
from .models import PasswordHistory # 💡 방금 만든 수첩 모델 가져오기

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
    username = forms.CharField(label="아이디", max_length=150)

    # 💡 1. 여기서 정보가 맞는지 먼저 깐깐하게 검사합니다!
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username and email:
            # DB에 아이디와 이메일이 모두 일치하는 유저가 있는지 찾아봅니다.
            user_exists = User.objects.filter(username=username, email=email).exists()
            
            if not user_exists:
                # 🚨 없다면? 여기서 에러를 발생시켜서 다음 페이지로 넘어가는 걸 멱살 잡고 막습니다!
                raise ValidationError("입력하신 아이디와 이메일 정보가 일치하는 회원을 찾을 수 없습니다.")
        
        return cleaned_data

    # 2. 메일 발송 유저 필터링 (기존 코드 그대로 유지)
    def get_users(self, email):
        active_users = super().get_users(email)
        input_username = self.cleaned_data.get('username')
        return (user for user in active_users if user.username == input_username)
class CustomSetPasswordForm(SetPasswordForm):
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password1')

        if new_password:
            # 1. '현재' 사용 중인 비밀번호와 일치하는지 검사
            if self.user.check_password(new_password):
                self.add_error('new_password1', "현재 사용 중인 비밀번호입니다. 새로운 비밀번호를 입력해 주세요.")
                return cleaned_data

            # 2. 💡 핵심 변경: 과거 기록 중 '최근 3개'만 잘라서 가져옵니다! (슬라이싱 [:3])
            # 모델에서 이미 -created_at(최신순) 정렬을 해두었기 때문에 그냥 [:3]만 붙이면 됩니다.
            recent_histories = PasswordHistory.objects.filter(user=self.user)[:3]
            for history in recent_histories:
                if check_password(new_password, history.password_hash):
                    self.add_error('new_password1', "최근에 사용했던 3개의 비밀번호는 다시 사용할 수 없습니다.")
                    break 

        return cleaned_data

    def save(self, commit=True):
        # 장고 원래 기능대로 비밀번호 변경
        user = super().save(commit)
        
        if commit:
            # 1. 새롭게 변경된 비밀번호를 수첩에 추가합니다.
            PasswordHistory.objects.create(user=user, password_hash=user.password)
            
            # 2. 💡 DB 최적화 (청소 기능): 최근 3개 기록의 ID만 남기고 나머지는 싹 다 지워버립니다!
            histories_to_keep = PasswordHistory.objects.filter(user=user).values_list('id', flat=True)[:3]
            PasswordHistory.objects.filter(user=user).exclude(id__in=histories_to_keep).delete()
            
        return user