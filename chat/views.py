from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from course.models import Course
from .models import Conversation, Message


def _is_teacher_of_course(user, course):
    # 강사 판별: 강의 담당 강사인지
    return course.teacher_id == user.id


def _is_student_of_course(user, course):
    # 수강생 판별: 해당 강의 수강생인지
    return course.students.filter(id=user.id).exists()


@login_required
def inbox(request):
    # 내(강사 또는 학생)가 포함된 대화방만 노출
    conversations = (
        Conversation.objects
        .filter(Q(teacher=request.user) | Q(student=request.user))
        .select_related("course", "teacher", "student")
        .order_by("-created_at")
    )

    # 템플릿에서 filter/exclude/count를 못 쓰는 상황 대비: unread_count를 여기서 계산
    for convo in conversations:
        convo.unread_count = (
            Message.objects
            .filter(conversation=convo, is_read=False)
            .exclude(sender=request.user)
            .count()
        )

    return render(request, "chat/inbox.html", {"conversations": conversations})


@login_required
def dm_room_course(request, course_id):
    """
    학생은 무조건 해당 강의 강사와만 1:1 대화 가능하도록 잠그는 엔드포인트.
    /chat/<course_id>/ 로 들어오면 /chat/<course_id>/<teacher_id>/ 로 강제 이동.
    """
    course = get_object_or_404(Course, id=course_id)

    # 학생이 아니면 이 엔드포인트를 쓸 이유가 없으니 inbox로 보냄
    if not _is_student_of_course(request.user, course):
        return redirect("chat:inbox")

    return redirect("chat:dm_room", course_id=course.id, other_user_id=course.teacher_id)


@login_required
def dm_room(request, course_id, other_user_id):
    course = get_object_or_404(Course, id=course_id)

    # 1) 강사 입장: other_user_id는 반드시 "해당 강의 수강생"이어야 함
    if _is_teacher_of_course(request.user, course):
        teacher = request.user

        # 다른 유저 id로 접근하면 여기서 바로 차단(강의 수강생만 허용)
        student = get_object_or_404(course.students, id=other_user_id)

        convo = Conversation.objects.filter(
            course=course,
            teacher=teacher,
            student=student
        ).first()

        # 강사는 자동 생성하지 않음(기존 정책 유지)
        if convo is None:
            return redirect("teacherpage:course_students", course_id=course.id)

    # 2) 학생 입장: other_user_id가 강사 id가 아니면 강사로 교정(완전 잠금)
    elif _is_student_of_course(request.user, course):
        student = request.user
        teacher = course.teacher

        if other_user_id != teacher.id:
            return redirect("chat:dm_room_course", course_id=course.id)

        # 학생은 접속 시 자동 생성
        convo, _ = Conversation.objects.get_or_create(
            course=course,
            teacher=teacher,
            student=student
        )
    else:
        return redirect("chat:inbox")

    # 방 입장 시: 상대가 보낸 안읽은 메시지를 읽음 처리
    Message.objects.filter(
        conversation=convo,
        is_read=False
    ).exclude(
        sender=request.user
    ).update(
        is_read=True,
        read_at=timezone.now()
    )

    # 메시지 전송
    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        if content:
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                content=content
            )
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
        },
    )