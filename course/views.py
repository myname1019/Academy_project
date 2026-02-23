from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Course
from .forms import CourseForm


# 1. 강의 목록
class CourseList(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'


# 2. 강의 상세
class CourseDetail(DetailView):
    model = Course
    template_name = 'course/course_detail.html'
    context_object_name = 'course'


# 3. 강의 생성 (로그인 필요 + teacher 자동 지정)
class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


# 4. 강의 수정 (작성자만 가능)
class CourseUpdate(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')

    def get_queryset(self):
        # 본인이 만든 강의만 수정 가능
        return Course.objects.filter(teacher=self.request.user)


# 5. 강의 삭제 (작성자만 가능)
@login_required
def course_delete(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk,
        teacher=request.user  # 본인 강의만 삭제 가능
    )

    if request.method == "POST":
        course.delete()
        return redirect('course:course_list')

    return redirect('course:course_detail', pk=pk)