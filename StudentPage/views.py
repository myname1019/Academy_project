from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from course.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('home')

    # POST 요청(자기소개 저장 버튼 클릭)이 들어왔을 때 처리
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        request.user.bio = new_bio  # 현재 로그인한 유저의 bio 필드 업데이트
        request.user.save()
        return redirect('student_dashboard')

    courses = request.user.student_courses.all()
    
    # 템플릿에서 쓸 'target_user'를 현재 로그인한 유저(본인)로 설정해서 보냄
    return render(request, 'studentpage/dashboard.html', {
        'courses': courses,
        'target_user': request.user  
    })

@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)

    if request.user not in course.students.all():
        course.students.add(request.user)

    return redirect('student_dashboard')