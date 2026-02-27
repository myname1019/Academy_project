from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from course.models import Course
from django.contrib.auth import get_user_model
from review.models import Review   # ✅ 반드시 있어야 함
from django.contrib import messages
from chat.models import Conversation, Message

User = get_user_model()


def student_dashboard(request):
    # 💡 1차 관문: 로그인을 안 했으면 403 에러 발생
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
        return redirect('main_page') # ⚠️ URL 이름이 'home'이라면 'home'으로 바꿔주세요!

    # 💡 2차 관문: 로그인은 했지만 학생(student)이 아니면 팝업 띄우고 튕겨냄
    if request.user.role != 'student':
        messages.error(request, "학생 계정으로 로그인해야 접근할 수 있는 페이지입니다.")
        return redirect('main_page')

    # 자기소개 저장
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        request.user.bio = new_bio
        request.user.save()
        messages.success(request, "자기소개가 저장되었습니다.")
        return redirect('studentpage:student_dashboard')

    # ✅ 수강 중 강의 가져오기 및 페이징 처리 (feature 브랜치 반영)
    all_courses = request.user.student_courses.all().order_by('-id')
    paginator = Paginator(all_courses, 6)  # 한 페이지에 6개씩 노출
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ✅ 내가 작성한 리뷰 통계
    user_reviews = Review.objects.filter(user=request.user)
    review_count = user_reviews.count()
    avg_rating = user_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # ✅ 내가 참여한 대화방 목록
    conversations = Conversation.objects.filter(
        Q(teacher=request.user) | Q(student=request.user)
    )

    # ✅ 내가 받은 안읽은 메시지 개수 (내가 보낸 건 제외)
    unread_count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(
        sender=request.user
    ).count()

    return render(request, 'studentpage/dashboard.html', {
        'courses': page_obj,
        'target_user': request.user,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1),
        'unread_count': unread_count,  # 🔴 추가됨
    })


def enroll_course(request, course_id):
    # 💡 1차 관문: 로그인을 안 했으면 팝업 띄우고 튕겨냄
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 수강 신청을 할 수 있습니다.")
        return redirect('main_page')

    # 💡 2차 관문: 로그인은 했지만 학생(student)이 아니면 팝업 띄우고 튕겨냄
    if request.user.role != 'student':
        messages.error(request, "학생 계정만 수강 신청이 가능합니다.")
        return redirect('main_page')

    course = get_object_or_404(Course, id=course_id)

    # 아직 수강 신청하지 않은 강의라면 신청 처리
    if request.user not in course.students.all():
        course.students.add(request.user)
        # 💡 성공적으로 신청되었을 때 초록색 체크 팝업 띄우기! (SweetAlert2의 success 아이콘으로 뜹니다)
        messages.success(request, f"'{course.title}' 수강 신청이 완료되었습니다!")

    # ✅ 올바른 URL 네임스페이스 사용 (othermain 브랜치 반영)
    return redirect('studentpage:student_dashboard')


# ✅ 결제 기능 (othermain 브랜치 반영)
def course_checkout(request, course_id):
    # 1. 로그인/학생 여부 확인
    if not request.user.is_authenticated or request.user.role != 'student':
        messages.error(request, "학생 계정만 결제할 수 있습니다.")
        return redirect('main_page')

    course = get_object_or_404(Course, id=course_id)

    # 2. 이미 수강 중인지 한 번 더 체크 (결제창 진입 방지)
    if request.user in course.students.all():
        messages.warning(request, "이미 수강 중인 강의입니다.")
        return redirect('studentpage:student_dashboard')

    # 3. 결제 창 템플릿 띄워주기
    return render(request, 'studentpage/checkout.html', {
        'course': course
    })