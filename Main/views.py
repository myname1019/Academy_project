from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from course.models import Course

# 1. 메인 페이지 (클래스형 뷰)
class MainPageView(ListView):
    model = Course
    template_name = 'Main/index.html'
    context_object_name = 'course_list'
    paginate_by = 8

    # 💡 1. 여기서 필터링이 제대로 되는지 확인!
    def get_queryset(self):
        # 기본적으로 모든 강의를 최신순으로 가져옵니다.
        queryset = Course.objects.all().order_by('-created_at')
        
        # 주소창에 ?subject=python 같은 값이 있는지 확인합니다.
        subject = self.request.GET.get('subject')
        
        # 💡 만약 과목이 선택되었다면, 해당 카테고리만 필터링합니다!
        if subject:
            queryset = queryset.filter(category=subject) # (모델의 필드 이름이 category가 맞는지 확인)
            
        return queryset

    # 💡 2. 페이지네이션과 화면 표시용 데이터
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 과목 이름 템플릿으로 넘기기
        subject = self.request.GET.get('subject')
        if subject:
            # 모델에 CATEGORY_CHOICES가 있다면 한글 이름을 가져옵니다.
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


# 2. 검색 페이지 (클래스형 뷰)
class SearchPageView(ListView):
    model = Course
    template_name = 'Main/search.html'
    context_object_name = 'course_list'


    # 💡 검색어 필터링 로직
    def get_queryset(self):
        queryset = Course.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '')
        
        if q:
            queryset = queryset.filter(title__icontains=q)
        else:
            # 검색어가 없으면 빈 리스트 반환
            queryset = Course.objects.none() 
        return queryset

    # 💡 화면에 넘겨줄 추가 데이터 (검색어)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context