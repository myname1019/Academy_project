from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
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


# 3. 강의 생성
class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')


# 4. 강의 수정
class CourseUpdate(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'course/course_form.html'
    success_url = reverse_lazy('course:course_list')


# 5. 강의 삭제
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        course.delete()
        return redirect('course:course_list')

    return redirect('course:course_detail', pk=pk)