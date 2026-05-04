from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from course.models import Course
# ✅ [추가] Board 앱의 Post 모델을 가져옵니다. (경로가 다르면 수정하세요)
from Board.models import Post 


# 1. 메인 페이지 (클래스형 뷰)
class MainPageView(ListView):
    model = Course
    template_name = 'Main/index.html'
    context_object_name = 'course_list'
    paginate_by = 8

    def get_queryset(self):
        queryset = Course.objects.all().order_by('-created_at')
        subject = self.request.GET.get('subject')
        
        if subject:
            queryset = queryset.filter(category=subject)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ✅ [추가] 최근 공지사항 5개 추출
        # category가 'notice'인 글을 최신순(-created_at)으로 상위 5개만 가져옵니다.
        context['recent_notices'] = Post.objects.filter(category='notice').order_by('-created_at')[:5]

        # ✅ [추가] 최근 게시글 5개 추출
        # category가 'community'인 글을 최신순으로 상위 5개만 가져옵니다.
        context['recent_posts'] = Post.objects.filter(category='community').order_by('-created_at')[:5]

        # 과목 이름 템플릿으로 넘기기
        subject = self.request.GET.get('subject')
        if subject:
            try:
                category_dict = dict(Course.CATEGORY_CHOICES)
                context['subject_display'] = category_dict.get(subject, subject)
            except AttributeError:
                context['subject_display'] = subject

        # 커스텀 그룹 페이지네이션 계산 로직
        page_obj = context.get('page_obj')
        if page_obj:
            paginator = context['paginator']
            current_page = page_obj.number
            total_pages = paginator.num_pages

            page_group = (current_page - 1) // 5
            start_page = page_group * 5 + 1
            end_page = min(start_page + 4, total_pages)

            context['custom_page_range'] = range(start_page, end_page + 1)
            context['prev_group_start'] = start_page - 5 if start_page > 1 else None
            context['next_group_start'] = start_page + 5 if start_page + 5 <= total_pages else None

        return context


# 2. 검색 페이지 (기존 유지)
class SearchPageView(ListView):
    model = Course
    template_name = 'Main/search.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        queryset = Course.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '')
        
        if q:
            queryset = queryset.filter(title__icontains=q)
        else:
            queryset = Course.objects.none() 
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context

from django.http import HttpResponse
import socket

def session_test_view(request):
    # 1. 세션에 방문 횟수(visit_count) 기록
    if 'visit_count' not in request.session:
        request.session['visit_count'] = 1
    else:
        request.session['visit_count'] += 1

    # 2. 현재 이 코드를 실행 중인 서버(EC2)의 프라이빗 IP 가져오기
    try:
        server_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        server_ip = "IP 확인 불가"

    # 3. 화면에 출력할 HTML 생성
    html = f"""
    <html>
    <head><title>Redis Session Test</title></head>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>🔄 로드밸런서 & Redis 세션 테스트</h2>
        <hr>
        <p><strong>현재 접속 중인 서버 IP (EC2):</strong> <span style="color: blue; font-size: 20px;">{server_ip}</span></p>
        <p><strong>내 세션 ID (Session Key):</strong> {request.session.session_key}</p>
        <p><strong>이 페이지 방문 횟수:</strong> <span style="color: red; font-size: 20px;">{request.session['visit_count']}</span></p>
        <hr>
        <p>💡 <b>테스트 방법:</b> F5(새로고침)를 여러 번 눌러보세요.<br>
        서버 IP는 ALB 라운드 로빈에 의해 <b>변경</b>될 수 있지만, <br>
        세션 ID는 <b>그대로 유지</b>되고 방문 횟수는 계속 <b>증가</b>한다면 Redis 세션 관리가 완벽하게 동작하는 것입니다!</p>
    </body>
    </html>
    """
    return HttpResponse(html)
