from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.views.decorators.http import require_POST

from common.forms import UserForm
from .models import Student, Teacher, CustomUser
from review.models import Review   # ⚠ review 앱 이름 확인 (review or reviews)
from .forms import ProfileUpdateForm 

# ✅ 회원가입
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # 1. CustomUser 저장
            user = form.save()

            # 2. 역할(role) 가져오기
            role = form.cleaned_data.get('role')

            # 3. 역할별 프로필 생성
            if role == 'student':
                Student.objects.create(user=user)
            elif role == 'teacher':
                Teacher.objects.create(user=user)

            # 4. 자동 로그인
            raw_password = form.cleaned_data.get('password1')
            auth_user = authenticate(
                request,
                username=user.username,
                password=raw_password
            )

            if auth_user is not None:
                login(request, auth_user)
                return redirect('/')

    else:
        form = UserForm()

    return render(request, 'common/signup.html', {'form': form})


# ✅ 역할별 마이페이지 이동
@login_required
def mypage_redirect(request):
    role = request.user.role

    if role == 'student':
        return redirect('/StudentPage/')
    elif role == 'teacher':
        return redirect('teacherpage:dashboard')
    else:
        # 🔥 역할 없는 소셜 유저 보호
        return redirect('common:social_signup_role')


# ✅ 프로필 페이지 (자기소개 수정 + 리뷰 통계)
@login_required
def profile_view(request, username):
    target_user = get_object_or_404(CustomUser, username=username)

    # 자기소개 수정
    if request.method == "POST":
        if request.user == target_user:
            bio = request.POST.get("bio")
            target_user.bio = bio
            target_user.save()
            messages.success(request, "자기소개가 수정되었습니다.")
            return redirect("profile", username=username)

    # 리뷰 통계
    reviews = Review.objects.filter(user=target_user)  # ⚠ Review 모델 필드 확인
    review_count = reviews.count()
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    if avg_rating:
        avg_rating = round(avg_rating, 1)

    context = {
        "target_user": target_user,
        "review_count": review_count,
        "avg_rating": avg_rating,
    }

    return render(request, "studentpage/dashboard.html", context)

@login_required
@require_POST
def delete_account(request):
    user = request.user

    # (선택) 소프트 삭제가 더 안전
    # user.is_active = False
    # user.save(update_fields=["is_active"])

    # 하드 삭제
    logout(request)
    user.delete()

    return redirect('/')


@login_required
def profile_edit(request):
    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,  # 프로필 이미지 때문에 필수
            instance=user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "내 정보가 수정되었습니다.")
            return redirect("common:profile", username=user.username)
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, "common/profile_edit.html", {
        "form": form
    })

User = get_user_model()

def find_username(request): # 이메일로 아이디 찾기
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            user = users.first()
            username = user.username
            masked_username = username
            return render(request, 'common/find_username.html', {
                'username': masked_username, 
                'email': email
            })
        else:
            messages.error(request, "해당 이메일로 가입된 계정이 없습니다.")
            return redirect('common:find_username')
            
    # GET 요청일 때 (처음 페이지에 접속했을 때)
    return render(request, 'common/find_username.html')

@login_required
def social_signup_role(request):

    # ✅ 이미 역할이 정해진 유저는 접근 차단
    if request.user.role:
        return redirect('/')

    if request.method == 'POST':
        role = request.POST.get('role')
        user = request.user

        if role not in ['student', 'teacher']:
            messages.error(request, "잘못된 접근입니다.")
            return redirect('/')

        # 1️⃣ role 저장
        user.role = role
        user.save()

        # 2️⃣ 역할별 프로필 생성
        if role == 'student':
            Student.objects.get_or_create(user=user)
        elif role == 'teacher':
            Teacher.objects.get_or_create(user=user)

        messages.success(request, f"{user.get_role_display()}, 환영합니다!")
        return redirect('/')

    return render(request, 'common/social_signup.html')