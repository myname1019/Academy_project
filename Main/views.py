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