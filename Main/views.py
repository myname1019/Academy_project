from django.shortcuts import render
from course.models import Course

# 1. 기존 메인 페이지 View (검색 기능 제거)
def main_page(request):
    course_list = Course.objects.all().order_by('-created_at')
    
    subject = request.GET.get('subject')
    if subject:
        course_list = course_list.filter(category=subject)
        
    context = {
        'course_list': course_list,
        'subject': subject 
    }
    return render(request, 'Main/index.html', context)

# 2. 💡 새로 추가하는 검색 전용 View
def search_page(request):
    q = request.GET.get('q', '') 
    course_list = Course.objects.all().order_by('-created_at')
    
    if q:
        course_list = course_list.filter(title__icontains=q)
    else:
        # 검색어가 없으면 빈 리스트를 반환하거나 전체를 보여줄 수 있습니다. (여기선 빈 리스트 처리)
        course_list = []

    context = {
        'course_list': course_list,
        'q': q,            
    }
    return render(request, 'Main/search.html', context)