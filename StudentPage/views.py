from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from course.models import Course

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('home')

    courses = request.user.student_courses.all()
    return render(request, 'studentpage/dashboard.html', {
        'courses': courses
    })


@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)

    if request.user not in course.students.all():
        course.students.add(request.user)

    return redirect('student_dashboard')