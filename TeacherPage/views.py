from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def teacher_dashboard(request):
    user = request.user  # User 객체
    courses = user.teacher_courses.all()  # ForeignKey related_name 활용

    return render(request, 'TeacherPage/dashboard.html', {
        'target_user': user,
        'courses': courses
    })