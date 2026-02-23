from django.shortcuts import render
from course.models import Course

# Create your views here.

def Main(request):
    return render(request, 'Main/index.html')

def main_page(request):
    # 1. 일단 모든 강의를 가져옵니다 (나중에 활성화)
    # course_list = Course.objects.all().order_by('-create_date')
    course_list = [] # 지금은 빈 리스트로 임시 처리
    
    # --- [1] 카테고리(과목) 필터링 ---
    subject = request.GET.get('subject')
    if subject:
        # 모델의 카테고리 필드명에 맞춰서 필터링 (예: category=subject)
        # course_list = course_list.filter(category=subject)
        pass
        
    # --- [2] 🔍 검색어(강의명) 필터링 ---
    q = request.GET.get('q', '') # 검색창에서 입력한 값('q')을 가져옵니다. 없으면 빈 문자열.
    if q:
        # 모델의 강의명 필드가 'title'이라고 가정할 때, title에 q가 포함된 것만 필터링
        # course_list = course_list.filter(title__icontains=q)
        pass

    context = {
        'course_list': course_list,
        'q': q, # 검색창에 내가 친 검색어가 그대로 남아있게 하려면 같이 넘겨줍니다.
    }
    return render(request, 'index.html', context)