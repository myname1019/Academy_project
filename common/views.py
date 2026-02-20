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
            # 폼을 저장하고, 방금 생성된 유저 객체를 'user' 변수에 담아둡니다.
            user = form.save() 
            
            # 2. 방금 가입한 유저가 선택한 역할(role)이 무엇인지 폼에서 꺼내옵니다.
            role = form.cleaned_data.get('role')
            
            # 3. 역할에 맞춰 전용 테이블(Student 또는 Teacher)에 1:1 짝꿍 데이터 생성
            if role == 'student':
                # Student 테이블에 user 정보를 넣어서 새로 생성
                Student.objects.create(user=user)
            elif role == 'teacher':
                # Teacher 테이블에 user 정보를 넣어서 새로 생성
                Teacher.objects.create(user=user)
            
            # 4. 명시적 인증 과정 및 자동 로그인 (이전과 동일)
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
    if request.user.role == 'student':
        return redirect('student_dashboard')  # 그대로 사용 가능
    elif request.user.role == 'teacher':
        return redirect('TeacherPage:teacher_dashboard')  # namespace 포함