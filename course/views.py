from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from django.core.exceptions import PermissionDenied
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

    # 💡 [추가] 수강생 여부 확인 로직
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # 현재 로그인한 유저가 이 강의의 수강생 목록에 있는지 확인
            context['is_enrolled'] = self.object.students.filter(id=self.request.user.id).exists()
        return context

class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect('main_page')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

class CourseUpdate(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect('main_page')
        course = self.get_object()
        if course.teacher != request.user:
            return redirect('course:course_detail', pk=course.pk)
        return super().dispatch(request, *args, **kwargs)

def course_delete(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
        return redirect('main_page')
    course = get_object_or_404(Course, pk=pk)
    if course.teacher != request.user:
        messages.error(request, "본인이 작성한 강의만 삭제할 수 있습니다.")
        return redirect('course:course_detail', pk=pk)
    if request.method == "POST":
        course.delete()
        messages.success(request, "강의가 성공적으로 삭제되었습니다.")
        return redirect('course:course_list')
    return redirect('course:course_detail', pk=pk)