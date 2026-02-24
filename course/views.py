from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Course
from .forms import CourseForm
from django.db.models import Avg, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

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

        # 5개씩 페이지 묶음 계산
        page_group = (current_page - 1) // 5
        start_page = page_group * 5 + 1
        end_page = min(start_page + 4, total_pages)

        context['custom_page_range'] = range(start_page, end_page + 1)
        
        # 이전/다음 그룹 점프 로직
        context['prev_group_start'] = start_page - 5 if start_page > 1 else None
        context['next_group_start'] = start_page + 5 if start_page + 5 <= total_pages else None
        
        return context
    
    def get_queryset(self):
        return (Course.objects
                .annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                ))

class CourseDetail(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'
    
    def get_queryset(self):
        return (Course.objects
                .annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                ))

class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

class CourseUpdate(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        if course.teacher != request.user:
            return redirect('course:course_detail', pk=course.pk)
        return super().dispatch(request, *args, **kwargs)

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.teacher != request.user:
        return redirect('course:course_detail', pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect('course:course_list')
    return redirect('course:course_detail', pk=pk)