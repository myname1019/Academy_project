# TeacherPage/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, Exists, OuterRef, Subquery, Value, IntegerField
from django.db.models.functions import Coalesce
from course.models import Course
from .forms import TeacherCourseForm
from common.permissions import is_teacher
from chat.models import Conversation, Message


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
                filter=Q(conversations__messages__is_read=False) & ~Q(conversations__messages__sender=request.user),
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

    # 🔔 강사가 안 읽은 메시지 수 (학생이 보낸 것만)
    unread_messages = Message.objects.filter(
        conversation__teacher=request.user,
        is_read=False,
    ).exclude(
        sender=request.user
    ).count()

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

    return render(
        request,
        "teacherpage/course_form.html",
        {"form": form, "mode": "edit", "course": course},
    )


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
    강사가 본인 강의 수강생 목록 보기
    - 학생이 먼저 문의 시작(메시지 1개 이상)한 경우만 has_chat=True
    - 학생별 안읽은 메시지 수(unread_count)를 ORM으로 한 번에 계산
    """
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    # 1) 학생이 먼저 시작한 대화 여부: 해당 강의/강사/학생 조합으로 "메시지가 존재"하면 True
    has_chat_exists = Message.objects.filter(
        conversation__course=course,
        conversation__teacher=request.user,
        conversation__student=OuterRef("pk"),
    )

    # 2) 학생별 unread_count 계산용 서브쿼리
    #    - 조건: (같은 강의/강사/학생) AND is_read=False AND sender != request.user(강사)
    unread_count_subquery = (
        Message.objects
        .filter(
            conversation__course=course,
            conversation__teacher=request.user,
            conversation__student=OuterRef("pk"),
            is_read=False,
        )
        .exclude(sender=request.user)
        .values("conversation__student")          # student_id로 그룹핑
        .annotate(c=Count("id"))                  # 메시지 개수
        .values("c")[:1]                          # 결과 1개만
    )

    # 3) 수강생 queryset에 has_chat, unread_count를 붙여서 한 번에 가져오기
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