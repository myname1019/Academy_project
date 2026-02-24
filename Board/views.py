from django.shortcuts import render

# Create your views here.
def board_list(request):
  return render(request, 'Board/index.html')

def notice_list(request):
    return render(request, 'notice_list.html') # 'Board/' 제거
