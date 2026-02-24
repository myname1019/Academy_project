from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied # 💡 403 에러를 위해 추가
from django.db.models import Avg
from course.models import Course
from django.contrib.auth import get_user_model
from review.models import Review   # ✅ 반드시 있어야 함

User = get_user_model()


def student_dashboard(request):
    # 💡 1차 관문: 로그인을 안 했으면 403 에러 발생
    if not request.user.is_authenticated:
        raise PermissionDenied

    # 💡 2차 관문: 로그인은 했지만 학생(student)이 아니면 홈으로 튕겨냄
    if request.user.role != 'student':
        return redirect('home') # (URL name이 'home'인지 본인의 urls.py를 꼭 확인해 주세요!)

    # 자기소개 저장
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        request.user.bio = new_bio
        request.user.save()
        return redirect('student_dashboard')

    # 수강 중 강의
    courses = request.user.student_courses.all()

    # ✅ 내가 작성한 리뷰 통계 (반드시 return 위에 있어야 함)
    user_reviews = Review.objects.filter(user=request.user)
    review_count = user_reviews.count()
    avg_rating = user_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    return render(request, 'studentpage/dashboard.html', {
        'courses': courses,
        'target_user': request.user,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1),
    })


def enroll_course(request, course_id):
    # 💡 1차 관문: 로그인을 안 했으면 403 에러 발생
    if not request.user.is_authenticated:
        raise PermissionDenied

    # 💡 2차 관문: 로그인은 했지만 학생(student)이 아니면 홈으로 튕겨냄
    if request.user.role != 'student':
        return redirect('home')

    course = get_object_or_404(Course, id=course_id)

    if request.user not in course.students.all():
        course.students.add(request.user)

    return redirect('student_dashboard')