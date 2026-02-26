from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied  # 💡 403 에러를 위해 추가
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg

from course.models import Course
from .models import Review
from .forms import ReviewForm


# 🔥 리뷰 작성
def review_create(request, course_id):
    # 1차: 비로그인 차단
    if not request.user.is_authenticated:
        raise PermissionDenied

    course = get_object_or_404(Course, id=course_id)

    # ✅ 강사(작성자) 차단
    if course.teacher == request.user:
        messages.error(request, "강사(작성자)는 본인 강의에 리뷰를 작성할 수 없습니다.")
        return redirect("course:course_detail", pk=course.id)

    # ✅ 수강생만 리뷰 작성 가능
    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, "수강 신청한 강의만 리뷰를 작성할 수 있습니다.")
        return redirect("course:course_detail", pk=course.id)

    # ✅ 이미 리뷰 작성했는지 체크
    if Review.objects.filter(course=course, user=request.user).exists():
        messages.error(request, "이미 이 강의에 리뷰를 작성했습니다.")
        return redirect("course:course_detail", pk=course.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.user = request.user
            review.save()
            messages.success(request, "리뷰가 등록되었습니다.")
            return redirect("course:course_detail", pk=course.id)
    else:
        form = ReviewForm()

    return render(
        request,
        "review/review_form.html",
        {
            "form": form,
            "course": course,
        },
    )


# 🔥 리뷰 수정
def review_update(request, pk):
    # 1차: 비로그인 차단
    if not request.user.is_authenticated:
        raise PermissionDenied

    review = get_object_or_404(Review, pk=pk)
    course = review.course

    # ✅ 수강생만 수정 가능 (수강 여부 재확인)
    if course.teacher == request.user:
        messages.error(request, "강사(작성자)는 리뷰를 수정할 수 없습니다.")
        return redirect("course:course_detail", pk=course.id)

    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, "수강 신청한 강의의 리뷰만 수정할 수 있습니다.")
        return redirect("course:course_detail", pk=course.id)

    # ✅ 본인만 수정 가능
    if review.user != request.user:
        messages.error(request, "본인의 리뷰만 수정할 수 있습니다.")
        return redirect("course:course_detail", pk=course.id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "리뷰가 수정되었습니다.")
            return redirect("course:course_detail", pk=course.id)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "review/review_form.html",
        {
            "form": form,
            "course": course,
        },
    )


# 🔥 리뷰 삭제
def review_delete(request, pk):
    # 1차: 비로그인 차단
    if not request.user.is_authenticated:
        raise PermissionDenied
    
    if request.method != "POST":
        raise PermissionDenied  # 또는 redirect로 처리해도 됨

    review = get_object_or_404(Review, pk=pk)
    course = review.course

    # ✅ 수강생만 삭제 가능 (수강 여부 재확인)
    if course.teacher == request.user:
        messages.error(request, "강사(작성자)는 리뷰를 삭제할 수 없습니다.")
        return redirect("course:course_detail", pk=course.id)

    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, "수강 신청한 강의의 리뷰만 삭제할 수 있습니다.")
        return redirect("course:course_detail", pk=course.id)

    # ✅ 본인만 삭제 가능
    if review.user != request.user:
        messages.error(request, "본인의 리뷰만 삭제할 수 있습니다.")
        return redirect("course:course_detail", pk=course.id)

    review.delete()
    messages.success(request, "리뷰가 삭제되었습니다.")
    return redirect("course:course_detail", pk=course.id)

@login_required
def my_reviews(request):
    qs = (
        Review.objects
        .filter(user=request.user)
        .select_related("course")   # ✅ 강의 정보 같이 가져오기
        .order_by("-created_at", "-id")
    )

    paginator = Paginator(qs, 4)  # 한 페이지 10개(원하면 바꿔)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "reviews": page_obj,
        "review_count": qs.count(),
        "avg_rating": qs.aggregate(avg=Avg("rating"))["avg"],
    }
    return render(request, "review/my_reviews.html", context)