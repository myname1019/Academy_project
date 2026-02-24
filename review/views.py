from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied # 💡 403 에러를 위해 추가
from django.contrib import messages
from course.models import Course
from .models import Review
from .forms import ReviewForm

# 🔥 리뷰 작성
def review_create(request, course_id):
    # 💡 1차 관문: 비로그인 유저 접근 차단 (403 에러)
    if not request.user.is_authenticated:
        raise PermissionDenied

    course = get_object_or_404(Course, id=course_id)

    # 이미 리뷰 작성했는지 체크
    if Review.objects.filter(course=course, user=request.user).exists():
        messages.error(request, "이미 이 강의에 리뷰를 작성했습니다.")
        return redirect('course:course_detail', pk=course.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.user = request.user
            review.save()
            return redirect('course:course_detail', pk=course.id)
    else:
        form = ReviewForm()

    return render(request, 'review/review_form.html', {
        'form': form,
        'course': course
    })


# 🔥 리뷰 수정
def review_update(request, pk):
    # 💡 1차 관문: 비로그인 유저 접근 차단
    if not request.user.is_authenticated:
        raise PermissionDenied

    review = get_object_or_404(Review, pk=pk)

    # 💡 2차 관문: 본인만 수정 가능 (기존 로직 유지 - 훌륭합니다!)
    if review.user != request.user:
        messages.error(request, "본인의 리뷰만 수정할 수 있습니다.")
        return redirect('course:course_detail', pk=review.course.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "리뷰가 수정되었습니다.")
            return redirect('course:course_detail', pk=review.course.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review/review_form.html', {
        'form': form,
        'course': review.course
    })


# 🔥 리뷰 삭제
def review_delete(request, pk):
    # 💡 1차 관문: 비로그인 유저 접근 차단
    if not request.user.is_authenticated:
        raise PermissionDenied

    review = get_object_or_404(Review, pk=pk)

    # 💡 2차 관문: 본인만 삭제 가능
    if review.user != request.user:
        messages.error(request, "본인의 리뷰만 삭제할 수 있습니다.")
        return redirect('course:course_detail', pk=review.course.id)

    course_id = review.course.id
    review.delete()
    messages.success(request, "리뷰가 삭제되었습니다.")

    return redirect('course:course_detail', pk=course_id)