# TeacherPage/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count

from course.models import Course
from .forms import TeacherCourseForm
from common.permissions import is_teacher


@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """
    강사 전용 대시보드
    - 내 강의만 조회
    - 강의별 수강생 수(student_count) 표시
    - 상단 통계(내 강의 수, 총 수강생 수 등)
    """

    courses = (
        Course.objects
        .filter(teacher=request.user)
        .annotate(student_count=Count("students", distinct=True))
        .order_by("-created_at")
    )

    total_courses = courses.count()

    total_students = (
        Course.objects
        .filter(teacher=request.user)
        .values("students")
        .distinct()
        .count()
    )

    total_enrollments = 0  # 현재 구조상 별도 신청 로그 없음

    context = {
        "courses": courses,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_students": total_students,
    }

    return render(request, "teacherpage/dashboard.html", context)


@login_required
@user_passes_test(is_teacher)
def create_course(request):
    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("teacherpage:dashboard")
    else:
        form = TeacherCourseForm()

    return render(request, "teacherpage/course_form.html", {
        "form": form,
        "mode": "create"
    })


@login_required
@user_passes_test(is_teacher)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect("teacherpage:dashboard")
    else:
        form = TeacherCourseForm(instance=course)

    return render(request, "teacherpage/course_form.html", {
        "form": form,
        "mode": "edit",
        "course": course,
    })


@login_required
@user_passes_test(is_teacher)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        course.delete()
        return redirect("teacherpage:dashboard")

    return render(request, "teacherpage/course_confirm_delete.html", {
        "course": course
    })