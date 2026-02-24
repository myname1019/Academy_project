from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied # 💡 403 에러 발생용
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test

from course.models import Course
from .forms import TeacherCourseForm
from common.permissions import is_teacher
from django.contrib import messages

def teacher_dashboard(request):
    """
    통합 강사 대시보드
    """
    # 💡 1. 비로그인 사용자이거나 강사가 아닌 경우를 한 번에 체크합니다.
    if not request.user.is_authenticated or request.user.role != 'teacher':
        
        messages.error(request, "강사 계정으로 로그인해야 접근할 수 있는 페이지입니다.")
        
        return redirect('main_page')

    # 내 강의 목록 + 수강생 수(Students M2M)
    courses = (
        Course.objects
        .filter(teacher=request.user)
        .annotate(student_count=Count("students", distinct=True))
        .order_by("-created_at")
    )

    total_courses = courses.count()

    # 총 수강생(중복 제거)
    total_students = (
        Course.objects
        .filter(teacher=request.user)
        .values("students")
        .distinct()
        .count()
    )

    # Enrollment 모델이 있으면 집계, 없으면 0
    total_enrollments = 0
    try:
        from course.models import Enrollment
        total_enrollments = Enrollment.objects.filter(course__teacher=request.user).count()
    except Exception:
        total_enrollments = 0

    # bio 저장(같은 페이지에서 POST)
    if request.method == "POST":
        request.user.bio = request.POST.get("bio", "")
        request.user.save()
        return redirect("teacherpage:dashboard")

    context = {
        "target_user": request.user,  # 템플릿 프로필 영역에서 씀
        "courses": courses,
        "my_courses": courses,
        "total_courses": total_courses,
        "total_students": total_students,
        "total_enrollments": total_enrollments,
    }
    return render(request, "teacherpage/dashboard.html", context)


def create_course(request):
    """
    강사가 강의 생성
    """
    if not request.user.is_authenticated or request.user.role != 'teacher':
        # 💡 2. 화면에 띄울 에러 메시지를 장전합니다.
        messages.error(request, "강사 계정으로 로그인해야 접근할 수 있는 페이지입니다.")
        # 💡 3. 메인 페이지로 돌려보냅니다.
        return redirect('main_page')

    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("teacherpage:dashboard")
    else:
        form = TeacherCourseForm()

    return render(request, "teacherpage/course_form.html", {"form": form, "mode": "create"})


def edit_course(request, course_id):
    """
    강사가 본인 강의 수정
    """
    # 💡 권한 검사
    if not request.user.is_authenticated or request.user.role != 'teacher':
        # 💡 2. 화면에 띄울 에러 메시지를 장전합니다.
        messages.error(request, "강사 계정으로 로그인해야 접근할 수 있는 페이지입니다.")
        # 💡 3. 메인 페이지로 돌려보냅니다.
        return redirect('main_page')

    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect("teacherpage:dashboard")
    else:
        form = TeacherCourseForm(instance=course)

    return render(
        request,
        "teacherpage/course_form.html",
        {"form": form, "mode": "edit", "course": course},
    )


def delete_course(request, course_id):
    """
    강사가 본인 강의 삭제
    """
    # 💡 권한 검사
    if not request.user.is_authenticated or request.user.role != 'teacher':
        # 💡 2. 화면에 띄울 에러 메시지를 장전합니다.
        messages.error(request, "강사 계정으로 로그인해야 접근할 수 있는 페이지입니다.")
        # 💡 3. 메인 페이지로 돌려보냅니다.
        return redirect('main_page')

    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        course.delete()
        return redirect("teacherpage:dashboard")

    return render(request, "teacherpage/course_confirm_delete.html", {"course": course})

@login_required
@user_passes_test(is_teacher)
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    students = course.students.all().order_by("username")

    return render(request, "teacherpage/course_students.html", {
        "course": course,
        "students": students,
    })