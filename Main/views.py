from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from course.models import Course

# 1. 메인 페이지 (클래스형 뷰)
class MainPageView(ListView):
    model = Course
    template_name = 'Main/index.html'
    context_object_name = 'course_list'
    paginate_by = 8

    def get_queryset(self):
        # 기본적으로 모든 강의를 최신순으로 가져옵니다.
        queryset = Course.objects.all().order_by('-created_at')
        
        # 주소창에 ?subject=python 같은 값이 있는지 확인합니다.
        subject = self.request.GET.get('subject')
        
        # 과목이 선택되었다면, 해당 카테고리만 필터링합니다.
        if subject:
            queryset = queryset.filter(category=subject)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 과목 이름 템플릿으로 넘기기
        subject = self.request.GET.get('subject')
        if subject:
            try:
                category_dict = dict(Course.CATEGORY_CHOICES)
                context['subject_display'] = category_dict.get(subject, subject)
            except AttributeError:
                context['subject_display'] = subject

        # ✅ 스마트 페이지네이션 로직 적용
        page_obj = context.get('page_obj')
        if page_obj:
            paginator = context['paginator']
            current_page = page_obj.number
            total_pages = paginator.num_pages

            # 5페이지 단위 그룹 계산
            page_group = (current_page - 1) // 5
            start_page = page_group * 5 + 1
            end_page = min(start_page + 4, total_pages)
            context['custom_page_range'] = range(start_page, end_page + 1)

            # 스마트 이전 타겟
            prev_group_start = start_page - 5 if start_page > 1 else None
            if prev_group_start:
                context['prev_target'] = prev_group_start
            elif page_obj.has_previous():
                context['prev_target'] = page_obj.previous_page_number()
            else:
                context['prev_target'] = None

            # 스마트 다음 타겟
            next_group_start = start_page + 5 if start_page + 5 <= total_pages else None
            if next_group_start:
                context['next_target'] = next_group_start
            elif page_obj.has_next():
                context['next_target'] = page_obj.next_page_number()
            else:
                context['next_target'] = None

        return context


# 2. 검색 페이지 (클래스형 뷰)
class SearchPageView(ListView):
    model = Course
    template_name = 'Main/search.html'
    context_object_name = 'course_list'

    # ✅ 검색어 필터링 로직 (완벽 복구)
    def get_queryset(self):
        queryset = Course.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '')
        
        if q:
            queryset = queryset.filter(title__icontains=q)
        else:
            # 💡 검색어가 없으면 빈 리스트 반환 (기존 로직 유지)
            queryset = Course.objects.none() 
        return queryset

    # 💡 화면에 넘겨줄 추가 데이터 (검색어)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context