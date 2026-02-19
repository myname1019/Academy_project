from django.shortcuts import render, redirect
from common.forms import UserForm
from django.contrib.auth import authenticate, login

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # 1. DB에 유저 정보 저장 (이때 학생/선생 role 데이터도 함께 저장됩니다)
            form.save() 
            
            # 2. 폼에서 입력받은 아이디와 원본 비밀번호(암호화 전)를 가져옵니다.
            # (form.cleaned_data는 검증이 끝난 안전한 데이터를 의미합니다)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            
            # 3. 명시적 인증 과정: 해당 아이디와 비밀번호를 가진 유저가 DB에 진짜 있는지 확인
            user = authenticate(request, username=username, password=raw_password)
            
            # 4. 인증이 성공적으로 끝났다면 로그인 처리 후 메인으로 이동
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = UserForm()
        
    return render(request, 'common/signup.html', {'form': form})