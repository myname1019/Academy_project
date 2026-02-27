from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required # 1. 로그인 필수 기능을 위해 추가
# 만약 아래 줄에서 에러가 난다면, models.py에 Post 모델을 아직 안 만드신 거예요!
try:
    from .models import Post
except ImportError:
    Post = None 

# ==========================================
# 0. 공통 및 메인 화면 (Main & Common)
# ==========================================

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


# ==========================================
# 1. 공지사항 관련 기능 (Notice Functions)
# ==========================================

def notice_list(request):
    # .all()이나 .filter() 뒤에 list()를 감싸는 것이 교재의 힌트입니다!
    notices = list(Post.objects.filter(category='notice').order_by('-created_at'))
    
    return render(request, 'board/notice_list.html', {
        'notice_list': notices,
    })

def notice_detail(request, post_id):
    # category가 'notice'이면서 전달받은 post_id와 일치하는 글을 가져옵니다.
    # 만약 해당 글이 없으면 404 에러 페이지를 보여줍니다.
    notice = get_object_or_404(Post, id=post_id, category='notice')
    
    return render(request, 'board/notice_detail.html', {
        'notice': notice
    })

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

@login_required(login_url='common:login')
def notice_edit(request, post_id):
    # 1. 수정할 공지사항이 있는지 확인
    post = get_object_or_404(Post, id=post_id, category='notice')
    
    # 2. 관리자가 아니면 못 고치게 상세 페이지로 돌려보내기
    if not request.user.is_staff:
        return redirect('Board:notice_detail', post_id=post.id)

    # 3. [저장] 버튼 눌렀을 때: 바뀐 제목과 내용을 DB에 저장
    if request.method == "POST":
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()  # 변경 내용 저장
        return redirect('Board:notice_detail', post_id=post.id)

    # 4. 처음 들어왔을 때: 기존 글 내용을 화면에 미리 채워주기
    return render(request, 'board/notice_form.html', {'post': post, 'mode': 'edit'})

@login_required(login_url='common:login')
def notice_delete(request, post_id):
    # 삭제할 공지사항 확인
    post = get_object_or_404(Post, id=post_id, category='notice')
    
    # 관리자만 삭제 가능
    if request.user.is_staff:
        post.delete()
        return redirect('Board:notice_list')
    
    # 관리자 아니면 그냥 상세페이지로 이동
    return redirect('Board:notice_detail', post_id=post.id)


# ==========================================
# 2. 자유게시판 관련 기능 (Community Functions)
# ==========================================

#@login_required(login_url='common:login')비로그인자가 게시판누르면 로그인창 가는거 주석처리
def community_list(request):
    # 공지사항 리스트와 똑같은 방식으로 데이터를 가져옵니다.
    if Post:
        posts = Post.objects.filter(category='community').order_by('-created_at')
    else:
        posts = []
    return render(request, 'board/community_list.html', {'community_list': posts})

def community_detail(request, post_id):
    # 누구나 글 번호만 알면 상세 내용을 볼 수 있습니다.
    post = get_object_or_404(Post, id=post_id, category='community')
    return render(request, 'board/community_detail.html', {'post': post})

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

@login_required(login_url='common:login')
def community_delete(request, post_id):
    # 1. URL로 전달받은 ID를 통해 해당 게시글을 DB에서 조회 (카테고리가 community인지 검증)
    post = get_object_or_404(Post, id=post_id, category='community')
    
    # 2. [보안 로직] 프론트엔드(버튼 숨김)와 별개로 서버측에서 '관리자 권한' 유무를 최종 확인
    # 주소창 직접 입력(Direct URL Access)을 통한 비인가자의 삭제 시도를 원천 차단하기 위함
    if request.user == post.author or request.user.is_staff: # 글쓴이 or 관리자 일때 삭제 허용
        post.delete()  # 관리자(Staff) 권한 확인 시에만 실제 데이터 삭제 수행
        return redirect('Board:community_list') # 삭제 완료 후 게시판 목록으로 리다이렉트
    
    # 3. [예외 처리] 관리자가 아닌 사용자가 접근했을 경우, 
    # 별도의 에러 노이즈 없이 상세 페이지로 복귀시켜 불필요한 혼란 방지 (Silent Reject)
    return redirect('Board:community_detail', post_id=post_id)

# 로그인한 자들만 수정하기
@login_required(login_url='common:login')# 로그인한 자들만 수정하기
def community_edit(request, post_id):
    # 1. [데이터 조회] 수정하려는 게시글이 DB에 존재하는지 확인 (카테고리 검증 포함)
    post = get_object_or_404(Post, id=post_id, category='community')
    
    # 2. [권한 검증] 현재 로그인한 유저가 실제 글을 쓴 주인(author)인지 확인
    # 본인이 아닌 사람이 URL 조작을 통해 타인의 글을 수정하는 것을 방지
    if request.user != post.author:
        from django.contrib import messages
        messages.error(request, "본인의 글만 수정할 수 있습니다.")
        return redirect('Board:community_detail', post_id=post.id)

    # 3. [데이터 처리] 사용자가 수정 후 '저장(등록)' 버튼을 눌렀을 때 (POST 방식)
    if request.method == "POST":
        post.title = request.POST.get('title')     # 입력한 새 제목 가져오기
        post.content = request.POST.get('content') # 입력한 새 내용 가져오기
        post.save()  # 기존 DB 레코드를 새로운 내용으로 업데이트(저장)
        
        # 수정한 내용을 바로 확인할 수 있도록 상세 페이지로 이동
        return redirect('Board:community_detail', post_id=post.id)

    # 4. [화면 렌더링] 처음 수정 버튼을 눌렀을 때 (GET 방식)
    # 기존 글의 내용(post)과 수정 모드임을 알리는 변수(mode)를 템플릿으로 전달
    return render(request, 'board/community_form.html', {'post': post, 'mode': 'edit'})