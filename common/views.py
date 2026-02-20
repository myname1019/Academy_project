from django.shortcuts import render, redirect
from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# 새로 분리해서 만든 모델들을 가져옵니다.
from .models import Student, Teacher 

def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # 1. DB에 CustomUser (공통 로그인 정보) 먼저 저장
            user = form.save() 
            
            # 2. 역할(role) 꺼내오기
            role = form.cleaned_data.get('role')
            
            # 3. 역할에 맞춰 Student 또는 Teacher 데이터 생성
            if role == 'student':
                Student.objects.create(user=user)
            elif role == 'teacher':
                Teacher.objects.create(user=user)
            
            # 4. 자동 로그인 과정
            raw_password = form.cleaned_data.get('password1')
            auth_user = authenticate(request, username=user.username, password=raw_password)
            
            if auth_user is not None:
                login(request, auth_user)
                return redirect('/')
    else:
        form = UserForm()
        
    return render(request, 'common/signup.html', {'form': form})

@login_required
def mypage_redirect(request):
    # 유저의 역할에 따라 각기 다른 대시보드로 리다이렉트합니다.
    if request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'teacher':
        # 💡 네임스페이스(TeacherPage:)가 포함된 정확한 경로를 사용합니다.
        return redirect('TeacherPage:teacher_dashboard')