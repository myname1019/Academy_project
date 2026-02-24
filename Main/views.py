from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from course.models import Course

# 1. 메인 페이지 (클래스형 뷰)
class MainPageView(ListView):
    model = Course
    template_name = 'Main/index.html'
    context_object_name = 'course_list'

    # 💡 카테고리 필터링 로직
    def get_queryset(self):
        # 기본적으로 최신순 정렬된 전체 목록을 가져옵니다.
        queryset = Course.objects.all().order_by('-created_at')
        subject = self.request.GET.get('subject')
        
        # subject 값이 있으면 필터링을 적용합니다.
        if subject:
            queryset = queryset.filter(category=subject)
        return queryset

    # 💡 화면에 넘겨줄 추가 데이터 (한글 카테고리명)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.request.GET.get('subject')
        subject_display = ""
        
        if subject:
            category_dict = dict(Course.CATEGORY_CHOICES)
            subject_display = category_dict.get(subject, subject)
            
        context['subject_display'] = subject_display
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