from django.shortcuts import render
from course.models import Course

def main_page(request):
    # 1. 모든 강의 가져오기
    # 💡 수정 포인트: 모델에 맞춰 'create_date'를 'created_at'으로 변경했습니다.
    # (참고: 모델의 Meta 클래스에 이미 최신순 정렬 설정이 있어서 .order_by()를 생략해도 최신순으로 나옵니다!)
    course_list = Course.objects.all().order_by('-created_at')
    
    # --- [1] 카테고리(과목) 필터링 ---
    subject = request.GET.get('subject')
    if subject:
        # 모델의 카테고리 필드명(category)에 맞춰서 정확히 필터링됩니다.
        course_list = course_list.filter(category=subject)
        
    # --- [2] 🔍 검색어(강의명) 필터링 ---
    q = request.GET.get('q', '') 
    if q:
        # 강의명(title)에 검색어(q)가 포함된(icontains) 것만 필터링합니다.
        course_list = course_list.filter(title__icontains=q)

    context = {
        'course_list': course_list,
        'q': q,            # 검색창에 친 검색어 유지용
        'subject': subject # 💡 추가: 현재 선택된 카테고리를 화면에 유지하기 위해 같이 넘겨줍니다.
    }
    
    # 기존에 있던 Main 함수와 합쳐서 이 함수 하나로 index.html을 보여주도록 통일했습니다.
    return render(request, 'Main/index.html', context)