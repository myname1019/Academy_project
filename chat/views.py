from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from course.models import Course
from .models import Conversation, Message


def _is_teacher_of_course(user, course):
    return course.teacher_id == user.id


def _is_student_of_course(user, course):
    return course.students.filter(id=user.id).exists()


@login_required
def inbox(request):
    conversations = (
        Conversation.objects
        .filter(Q(teacher=request.user) | Q(student=request.user))
        .select_related("course", "teacher", "student")
        .order_by("-created_at")
    )
    return render(request, "chat/inbox.html", {"conversations": conversations})


@login_required
def dm_room(request, course_id, other_user_id):
    course = get_object_or_404(Course, id=course_id)

    # 강사 → 해당 강의 수강생만
    if _is_teacher_of_course(request.user, course):
        teacher = request.user
        student = get_object_or_404(course.students, id=other_user_id)

    # 학생 → 해당 강의 강사만
    elif _is_student_of_course(request.user, course):
        student = request.user
        teacher = course.teacher
        if teacher.id != other_user_id:
            return redirect("chat:inbox")

    else:
        return redirect("chat:inbox")

    convo, _ = Conversation.objects.get_or_create(course=course, teacher=teacher, student=student)

    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        if content:
            Message.objects.create(conversation=convo, sender=request.user, content=content)
        return redirect("chat:dm_room", course_id=course.id, other_user_id=other_user_id)

    messages = convo.messages.select_related("sender").all()

    return render(
        request,
        "chat/dm_room.html",
        {
            "course": course,
            "conversation": convo,
            "messages": messages,
            "teacher": teacher,
            "student": student,
            "other_user_id": other_user_id,
        },
    )