from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Course
from .forms import CourseForm

# 1. 강의 목록 (페이징 및 5개씩 페이지 그룹 처리 포함)
class CourseList(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    paginate_by = 3  # 한 페이지에 10개 강의

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_obj = context['page_obj']

        current_page = page_obj.number
        total_pages = paginator.num_pages

        # 5개씩 페이지 묶음 계산 (예: 1~5, 6~10, 11~15 ...)
        page_group = (current_page - 1) // 5
        start_page = page_group * 5 + 1
        end_page = min(start_page + 4, total_pages)

        context['custom_page_range'] = range(start_page, end_page + 1)
        return context

# 2. 강의 상세
class CourseDetail(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'

# 3. 강의 생성 (teacher 자동 저장)
class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

# 4. 강의 수정 (수정 권한 체크)
class CourseUpdate(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        if course.teacher != request.user:
            return redirect('course:course_detail', pk=course.pk)
        return super().dispatch(request, *args, **kwargs)

# 5. 강의 삭제 (수정 권한 체크)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if course.teacher != request.user:
        return redirect('course:course_detail', pk=pk)

    if request.method == "POST":
        course.delete()
        return redirect('course:course_list')

    return redirect('course:course_detail', pk=pk)