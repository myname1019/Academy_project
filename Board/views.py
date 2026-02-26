from django.shortcuts import render, redirect, get_object_or_404
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
    # 1. DB에서 공지사항(category='notice')만 최신순으로 가져오기
    if Post:
        # 필터링해서 가져온 데이터를 'notice_list'라는 이름으로 템플릿에 전달
        notices = Post.objects.filter(category='notice').order_by('-created_at')
    else:
        notices = []
    
    # 2. 템플릿(HTML)으로 데이터 보따리(Context) 전달
    return render(request, 'board/notice_list.html', {'notice_list': notices})

def community_list(request):
    return render(request, 'board/community_list.html')
# ✅ 새 기능: 관리자 전용 글쓰기 진입로
def notice_create(request):
    if not request.user.is_staff:
        raise Http404()

    # [등록하기] 버튼을 눌렀을 때만 실행되는 저장 로직
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if Post:
            Post.objects.create(
                title=title,
                content=content,
                category='notice',
                author=request.user
            )
            return redirect('Board:notice_list') # 저장 후 목록으로 이동

    return render(request, 'board/notice_form.html') # 버튼 안 눌렀을 땐 입력창 보여주기

# Board/views.py 맨 밑에 추가
def notice_detail(request, post_id):
    # 임시로 글 번호만 띄워봅니다.
    from django.http import HttpResponse
    return HttpResponse(f"{post_id}번 공지사항 상세 페이지 준비 중입니다.")
