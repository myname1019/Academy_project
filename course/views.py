from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from django.core.exceptions import PermissionDenied # 💡 403 에러 발생용

from django.contrib import messages
from .models import Course
from .forms import CourseForm


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

        page_group = (current_page - 1) // 5
        start_page = page_group * 5 + 1
        end_page = min(start_page + 4, total_pages)

        context['custom_page_range'] = range(start_page, end_page + 1)
        context['prev_group_start'] = start_page - 5 if start_page > 1 else None
        context['next_group_start'] = start_page + 5 if start_page + 5 <= total_pages else None

        return context

    def get_queryset(self):
        return (
            Course.objects
            .annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
            .order_by('-created_at')
        )


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
