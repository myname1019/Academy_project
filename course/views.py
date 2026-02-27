from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from django.core.exceptions import PermissionDenied
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
        
        context['custom_page_range'] = range(start_page, end_page + 1)
        
        # [스마트 페이징 로직 적용]
        # 1. 이전 버튼 목적지: 이전 그룹 시작점이 있으면 거기로, 없으면 바로 전 페이지로
        prev_group_start = start_page - 5 if start_page > 1 else None
        if prev_group_start:
            context['prev_target'] = prev_group_start
        elif page_obj.has_previous():
            context['prev_target'] = page_obj.previous_page_number()
        else:
            context['prev_target'] = None

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

    def dispatch(self, request, *args, **kwargs):
        # 1️⃣ 로그인 안 했으면 차단
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect('main_page')

        # 2️⃣ 학생이면 차단 (ohu 브랜치 로직 채택)
        if request.user.role != "teacher":
            messages.error(request, "선생님 계정만 강의 생성이 가능합니다.")
            return redirect('course:course_list')

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

# ===== 여기서부터 ohu 브랜치에서 추가된 대시보드 뷰입니다 =====

class MyTeachingCourseList(ListView):
    model = Course
    template_name = "course/course_board_list.html"
    context_object_name = "courses"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect("main_page")

        if request.user.role != "teacher":
            messages.error(request, "선생님 계정만 접근 가능합니다.")
            return redirect("course:course_list")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user).order_by("-created_at", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "내 강의 목록"
        context["mode"] = "teacher"

        page_obj = context.get("page_obj")
        courses = context.get("courses", [])

        if page_obj:
            total = page_obj.paginator.count
            start0 = page_obj.start_index() - 1  # 0-based
            context["course_rows"] = [
                (total - (start0 + i), course)
                for i, course in enumerate(courses)
            ]
        else:
            context["course_rows"] = []

        return context


class MyEnrolledCourseList(ListView):
    model = Course
    template_name = "course/course_board_list.html"
    context_object_name = "courses"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "로그인 후 이용할 수 있는 페이지입니다.")
            return redirect("main_page")

        if request.user.role != "student":
            messages.error(request, "학생 계정만 접근 가능합니다.")
            return redirect("course:course_list")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.student_courses.all().order_by("-created_at", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "내 수강 목록"
        context["mode"] = "student"

        page_obj = context.get("page_obj")
        courses = context.get("courses", [])

        if page_obj:
            total = page_obj.paginator.count
            start0 = page_obj.start_index() - 1  # 0-based
            context["course_rows"] = [
                (total - (start0 + i), course)
                for i, course in enumerate(courses)
            ]
        else:
            context["course_rows"] = []

        return context
    
# course/views.py (맨 아래에 추가)
from .forms import CourseForm, LessonForm # 💡 LessonForm 꼭 임포트!

def lesson_add(request, course_id):
    # 어떤 강의에 영상을 추가할지 찾습니다.
    course = get_object_or_404(Course, id=course_id)

    # 🚨 보안 1차 관문: 강사 본인만 영상 추가 가능
    if request.user != course.teacher:
        messages.error(request, "본인의 강의에만 영상을 추가할 수 있습니다.")
        return redirect('course:course_detail', pk=course.id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course # 💡 방금 찾은 강의(Course)와 이 영상(Lesson)을 연결!
            lesson.save()
            messages.success(request, f"'{lesson.title}' 영상이 추가되었습니다.")
            return redirect('course:course_detail', pk=course.id)
    else:
        form = LessonForm()

    return render(request, 'course/lesson_form.html', {
        'form': form,
        'course': course
    })