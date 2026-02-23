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
    - 강의별 수강생 수(student_count) 표시 (Course.students ManyToMany 기준)
    - 상단 통계(내 강의 수, 총 수강생 수 등) 표시
    """

    # 내 강의 목록 + 강의별 수강생 수 집계
    courses = (
        Course.objects
        .filter(teacher=request.user)
        .annotate(student_count=Count("students", distinct=True))
        .order_by("-created_at")
    )

    # 상단 통계: 내 강의 수
    total_courses = courses.count()

    # 총 수강생 수: 내가 만든 강의들에 속한 학생(중복 제거)
    total_students = (
        Course.objects
        .filter(teacher=request.user)
        .values("students")
        .distinct()
        .count()
    )

    # Enrollment 모델이 없으니 "총 수강신청 수"는 지금 구조에서는 동일하게 만들기 애매함
    # (신청 로그/날짜/상태 같은 기록이 없어서)
    # 포트폴리오에서 보여줄 값이 필요하면, 일단 0으로 두거나 템플릿에서 숨기는 게 안전함.
    total_enrollments = 0

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
    """
    강사가 강의 생성
    - teacher는 자동으로 request.user로 저장
    - 썸네일 업로드(request.FILES) 지원
    """
    if request.method == "POST":
        form = TeacherCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user  # 강사 자동 연결
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