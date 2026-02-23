from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from course.models import Course
from .models import Review
from .forms import ReviewForm


# 🔥 리뷰 작성
@login_required
def review_create(request, course_id):
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
@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)

    # 본인만 수정 가능
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
@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)

    # 본인만 삭제 가능
    if review.user != request.user:
        messages.error(request, "본인의 리뷰만 삭제할 수 있습니다.")
        return redirect('course:course_detail', pk=review.course.id)

    course_id = review.course.id
    review.delete()
    messages.success(request, "리뷰가 삭제되었습니다.")

    return redirect('course:course_detail', pk=course_id)