# TeacherPage/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, Exists, OuterRef, Subquery, Value, IntegerField
from django.db.models.functions import Coalesce

from course.models import Course
from .forms import TeacherCourseForm
from common.permissions import is_teacher
from chat.models import Message


@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    courses = (
        Course.objects
        .filter(teacher=request.user)
        .annotate(student_count=Count("students", distinct=True))
        .annotate(
            unread_chat_count=Count(
                "conversations__messages",
                filter=Q(conversations__messages__is_read=False)
                       & ~Q(conversations__messages__sender=request.user),
                distinct=True,
            )
        )
        .order_by("-created_at")
    )

    total_courses = courses.count()
    total_students = (
        Course.objects
        .filter(teacher=request.user)
        .exclude(students__isnull=True)
        .values_list("students", flat=True)
        .distinct()
        .count()
    )

    unread_messages = (
        Message.objects
        .filter(conversation__teacher=request.user, is_read=False)
        .exclude(sender=request.user)
        .count()
    )

    if request.method == "POST":
        request.user.bio = request.POST.get("bio", "")
        request.user.save()
        return redirect("teacherpage:dashboard")

    context = {
        "target_user": request.user,
        "my_courses": courses,
        "total_courses": total_courses,
        "total_students": total_students,
        "unread_messages": unread_messages,
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

    return render(request, "teacherpage/course_form.html", {"form": form, "mode": "create"})


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

    return render(request, "teacherpage/course_confirm_delete.html", {"course": course})


@login_required
@user_passes_test(is_teacher)
def course_students(request, course_id):
    """
    강의별 수강생 목록
    - 학생이 먼저 문의 시작(메시지 1개 이상)한 경우만 has_chat=True
    - 학생별 안읽은 메시지 수(unread_count)
    """
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    has_chat_exists = Message.objects.filter(
        conversation__course=course,
        conversation__teacher=request.user,
        conversation__student=OuterRef("pk"),
    )

    unread_count_subquery = (
        Message.objects
        .filter(
            conversation__course=course,
            conversation__teacher=request.user,
            conversation__student=OuterRef("pk"),
            is_read=False,
        )
        .exclude(sender=request.user)
        .values("conversation__student")
        .annotate(c=Count("id"))
        .values("c")[:1]
    )

    students_qs = (
        course.students
        .all()
        .order_by("username")
        .annotate(
            has_chat=Exists(has_chat_exists),
            unread_count=Coalesce(
                Subquery(unread_count_subquery, output_field=IntegerField()),
                Value(0),
            ),
        )
    )

    context = {
        "course": course,
        "students": students_qs,
        "student_count": students_qs.count(),
    }
    return render(request, "teacherpage/course_students.html", context)


@login_required
@user_passes_test(is_teacher)
def students_all(request):
    """
    전체 수강생(중복 제거) + 관리자 느낌
    - 학생별 수강 강의 목록
    - has_chat(학생이 먼저 문의 시작했는지)
    - unread_total(학생이 보낸 안읽은 메시지 총합)
    """
    User = get_user_model()

    # 전체 수강생 id
    student_ids = (
        Course.objects
        .filter(teacher=request.user)
        .values_list("students__id", flat=True)
        .exclude(students__isnull=True)
        .distinct()
    )

    # 학생 queryset
    students = (
        User.objects
        .filter(id__in=student_ids)
        .only("id", "username", "first_name", "email")
        .order_by("username")
    )

    # 학생별 수강 강의 매핑: {student_id: [{id,title}, ...]}
    courses_by_student = {}
    rows = (
        Course.objects
        .filter(teacher=request.user, students__in=students)
        .values("id", "title", "students__id")
        .order_by("-created_at")
    )
    for r in rows:
        sid = r["students__id"]
        courses_by_student.setdefault(sid, []).append({
            "id": r["id"],
            "title": r["title"],
        })

    # has_chat / unread_total
    has_chat_exists = Message.objects.filter(
        conversation__teacher=request.user,
        conversation__student=OuterRef("pk"),
    )

    unread_total_subq = (
        Message.objects
        .filter(
            conversation__teacher=request.user,
            conversation__student=OuterRef("pk"),
            is_read=False,
        )
        .exclude(sender=request.user)
        .values("conversation__student")
        .annotate(c=Count("id"))
        .values("c")[:1]
    )

    students = students.annotate(
        has_chat=Exists(has_chat_exists),
        unread_total=Coalesce(
            Subquery(unread_total_subq, output_field=IntegerField()),
            Value(0),
        ),
    )

    context = {
        "target_user": request.user,
        "students": students,
        "student_count": students.count(),
        "courses_by_student": courses_by_student,
    }
    return render(request, "teacherpage/students_all.html", context)