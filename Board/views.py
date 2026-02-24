from django.shortcuts import render
from django.http import Http404
# 만약 아래 줄에서 에러가 난다면, models.py에 Post 모델을 아직 안 만드신 거예요!
try:
    from .models import Post
except ImportError:
    Post = None 

def board_list(request):
    # Post 모델이 있고, 실제 DB에 테이블이 생성되었을 때만 데이터를 가져옵니다.
    if Post:
        try:
            notices = Post.objects.filter(category='notice').order_by('-created_at')[:5]
            communities = Post.objects.filter(category='community').order_by('-created_at')[:5]
        except: # 테이블이 아직 생성 안 된 경우 대비
            notices = []
            communities = []
    else:
        notices = []
        communities = []

    # 아까 index.html을 Board 폴더 밖으로 꺼내셨다면 'index.html'로 수정!
    # 폴더 안에 그대로 두셨다면 'Board/index.html' 유지!
    return render(request, 'Board/index.html', {
        'notices': notices,
        'communities': communities
    })

def notice_list(request):
    return render(request, 'notice_list.html')

def community_list(request):
    return render(request, 'community_list.html')
# ✅ 새 기능: 관리자 전용 글쓰기 진입로
def notice_create(request):
    # 1. 관리자(is_staff)가 아니면 "페이지 없음"으로 속여서 존재를 숨김
    if not request.user.is_staff:
        raise Http404()
    
    # 2. 관리자일 때만 아래 화면을 보여줌
    # (notice_form.html 이라는 이름의 새 파일을 만드셔야 합니다)
    return render(request, 'notice_form.html')
