from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required # 1. 로그인 필수 기능을 위해 추가
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
    # .all()이나 .filter() 뒤에 list()를 감싸는 것이 교재의 힌트입니다!
    notices = list(Post.objects.filter(category='notice').order_by('-created_at'))
    
    return render(request, 'board/notice_list.html', {
        'notice_list': notices,
        
    })
    
@login_required(login_url='common:login')
def community_list(request):
    # 공지사항 리스트와 똑같은 방식으로 데이터를 가져옵니다.
    if Post:
        posts = Post.objects.filter(category='community').order_by('-created_at')
    else:
        posts = []
    return render(request, 'board/community_list.html', {'community_list': posts})
def notice_create(request):
    if not request.user.is_staff:
        raise Http404()

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
            return redirect('Board:notice_list')

    return render(request, 'board/notice_form.html')

def notice_detail(request, post_id):
    # category가 'notice'이면서 전달받은 post_id와 일치하는 글을 가져옵니다.
    # 만약 해당 글이 없으면 404 에러 페이지를 보여줍니다.
    notice = get_object_or_404(Post, id=post_id, category='notice')
    
    return render(request, 'board/notice_detail.html', {
        'notice': notice
    })
@login_required(login_url='common:login')
def community_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if Post:
            Post.objects.create(
                title=title,
                content=content,
                category='community',
                author=request.user  # ✅ 바로 이 줄! 접속한 '나'를 작성자로 저장합니다.
            )
            return redirect('Board:community_list')
    return render(request, 'board/community_form.html')

# Board/views.py 에 이 함수가 있는지 꼭 확인하세요!

def community_detail(request, post_id):
    # 1. 일단 해당 번호의 게시글을 가져옵니다. 없으면 404 에러!
    post = get_object_or_404(Post, id=post_id, category='community')
    
    # 2. 로그인 여부 확인
    if not request.user.is_authenticated:
        return render(request, 'board/community_list.html', {
            'community_list': Post.objects.filter(category='community'),
            'error_message': "로그인한 사람만 볼 수 있습니다."
        })
    
    # 3. 로그인했다면 상세 페이지 보여주기
    return render(request, 'board/community_detail.html', {'post': post})

# 이 아래에 아까 만든 community_delete 함수가 이어져야 합니다.





@login_required(login_url='common:login')
def community_delete(request, post_id):
    # 1. 삭제할 게시글 가져오기 (없으면 404)
    post = get_object_or_404(Post, id=post_id, category='community')
    
    # 2. 권한 체크: 글쓴이 본인이거나 관리자(is_staff)인 경우만 삭제 가능
    if request.user == post.author or request.user.is_staff:
        post.delete()
        return redirect('Board:community_list')
    else:
        # 권한이 없는 경우 (남의 글을 주소창 입력으로 지우려 할 때)
        from django.contrib import messages
        messages.error(request, "삭제 권한이 없습니다.")
        return redirect('Board:community_detail', post_id=post_id)