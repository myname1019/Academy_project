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
    통합 강사 대시보드
    - 프로필(자기소개 bio) + 강의관리 + 통계 + 썸네일 카드
    """

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
        "total_courses": total_courses,
        "total_students": total_students,
        "total_enrollments": total_enrollments,
    }
    return render(request, "teacherpage/dashboard.html", context)


@login_required
@user_passes_test(is_teacher)
def create_course(request):
    """
    강사가 강의 생성
    - teacher는 자동으로 request.user로 저장
    - 썸네일 업로드(request.FILES) 지원
    """
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


@login_required
@user_passes_test(is_teacher)
def edit_course(request, course_id):
    """
    강사가 본인 강의 수정
    """
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


@login_required
@user_passes_test(is_teacher)
def delete_course(request, course_id):
    """
    강사가 본인 강의 삭제
    - GET: 확인 화면
    - POST: 실제 삭제
    """
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        course.delete()
        return redirect("teacherpage:dashboard")

    return render(request, "teacherpage/course_confirm_delete.html", {"course": course})