from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator  # 💡 페이징을 위해 추가
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from course.models import Course
from django.contrib.auth import get_user_model
from review.models import Review
from django.contrib import messages

User = get_user_model()

def student_dashboard(request):
    # 1차 관문: 로그인을 안 했으면 팝업 띄우고 튕겨냄
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
        return redirect('main_page')

    # 2차 관문: 학생(student)이 아니면 팝업 띄우고 튕겨냄
    if request.user.role != 'student':
        messages.error(request, "학생 계정으로 로그인해야 접근할 수 있는 페이지입니다.")
        return redirect('main_page')

    # 자기소개 저장 (POST 요청 시)
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        request.user.bio = new_bio
        request.user.save()
        messages.success(request, "자기소개가 저장되었습니다.")
        return redirect('StudentPage:student_dashboard')

    # ✅ 수강 중 강의 가져오기 및 페이징 처리
    all_courses = request.user.student_courses.all().order_by('-id')
    paginator = Paginator(all_courses, 6) # 한 페이지에 6개씩 노출
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 내가 작성한 리뷰 통계
    user_reviews = Review.objects.filter(user=request.user)
    review_count = user_reviews.count()
    avg_rating = user_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    return render(request, 'studentpage/dashboard.html', {
        'courses': page_obj,  # 💡 페이징 객체를 템플릿으로 전달
        'target_user': request.user,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1),
    })

def enroll_course(request, course_id):
    # 1차 관문: 비로그인 처리
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 수강 신청을 할 수 있습니다.")
        return redirect('main_page')

    # 2차 관문: 권한 체크
    if request.user.role != 'student':
        messages.error(request, "학생 계정만 수강 신청이 가능합니다.")
        return redirect('main_page')

    course = get_object_or_404(Course, id=course_id)

    # 아직 수강 신청하지 않은 강의라면 신청 처리
    if request.user not in course.students.all():
        course.students.add(request.user)
        messages.success(request, f"'{course.title}' 수강 신청이 완료되었습니다!")

    # 💡 네임스페이스 포함하여 리다이렉트 (오류 해결 지점)
    return redirect('StudentPage:student_dashboard')