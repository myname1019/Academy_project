from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from django.core.exceptions import PermissionDenied # 💡 403 에러 발생용

from django.contrib import messages
from .models import Course
from .forms import CourseForm
from django.core.paginator import Paginator


class CourseList(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_obj = context['page_obj']

        current_page = page_obj.number
        total_pages = paginator.num_pages
        subject = self.request.GET.get('subject')
        
        subject_map = {
            'korean': '국어', 'math': '수학', 'english': '영어',
            'social': '사회', 'science': '과학', 'etc': '기타'
        }
        context['subject_display'] = subject_map.get(subject)
        
        # 5페이지 단위 그룹 계산
        page_group = (current_page - 1) // 5
        start_page = page_group * 5 + 1
        end_page = min(start_page + 4, total_pages)

        # 2. 다음 버튼 목적지: 다음 그룹 시작점이 있으면 거기로, 없으면 바로 다음 페이지로
        next_group_start = start_page + 5 if start_page + 5 <= total_pages else None
        if next_group_start:
            context['next_target'] = next_group_start
        elif page_obj.has_next():
            context['next_target'] = page_obj.next_page_number()
        else:
            context['next_target'] = None
        
        subject = self.request.GET.get('subject')
        subject_map = {
            'korean': '국어',
            'math': '수학',
            'english': '영어',
            'social': '사회',
            'science': '과학',
            'etc': '기타',
        }
        # {{ subject_display }}로 템플릿에서 한글 이름을 쓸 수 있게 함
        context['subject_display'] = subject_map.get(subject)
        return context

    def get_queryset(self):
        # 1. URL에서 파라미터 가져오기
        subject = self.request.GET.get('subject')
        q = self.request.GET.get('q')

        # 2. 기본 쿼리셋 (리뷰 등 계산 포함)
        queryset = Course.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-created_at')

        # 3. 과목(subject) 필터링 (핵심!)
        if subject and subject != 'all':
            queryset = queryset.filter(category=subject) # 모델 필드명에 주의!

        if q:
            queryset = queryset.filter(title__icontains=q)

        return queryset
    
    

from django.core.paginator import Paginator  # ✅ 추가


class CourseDetail(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return (
            Course.objects
            .annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ 기존 is_enrolled 유지 (그대로)
        if self.request.user.is_authenticated:
            context['is_enrolled'] = self.object.students.filter(id=self.request.user.id).exists()
        else:
            context['is_enrolled'] = False  # ✅ 추가(템플릿에서 안전)

        # ✅ 리뷰 5개씩 페이징만 추가(핵심)
        reviews = self.object.reviews.all().order_by('-created_at', '-id')
        paginator = Paginator(reviews, 3)
        context['reviews_page'] = paginator.get_page(self.request.GET.get('rpage'))

        return context

class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    # 💡 3. CourseCreate: 비로그인 유저 접근 방지
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect('main_page')  # 💡 로그인 페이지로 보내려면 'common:login' 등으로 변경하세요!
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class CourseUpdate(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    # 💡 4. CourseUpdate: 비로그인 방지 + 본인(작성자) 확인 로직 병합
    def dispatch(self, request, *args, **kwargs):
        # 1차 관문: 로그인을 안 했으면 팝업 띄우고 메인으로
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect('main_page')
            
        course = self.get_object()
        
        # 2차 관문: 로그인은 했지만 본인이 올린 강의가 아니면 상세 페이지로 튕겨냄
        if course.teacher != request.user:
            return redirect('course:course_detail', pk=course.pk)
            
        return super().dispatch(request, *args, **kwargs)


# 💡 5. course_delete (함수형 뷰)
def course_delete(request, pk):
    # 1차 관문: 로그인을 안 했으면 403 에러
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
        return redirect('main_page')

    course = get_object_or_404(Course, pk=pk)
    
    # 2차 관문: 로그인은 했지만 본인이 올린 강의가 아니면 상세 페이지로 튕겨냄
    if course.teacher != request.user:
        messages.error(request, "본인이 작성한 강의만 삭제할 수 있습니다.")
        return redirect('course:course_detail', pk=pk)
        
    if request.method == "POST":
        course.delete()
        messages.success(request, "강의가 성공적으로 삭제되었습니다.") # 💡 삭제 성공 팝업 (선택사항)
        return redirect('course:course_list')
    
    return redirect('course:course_detail', pk=pk)
