from django.shortcuts import render

def home(request):
    return render(request, 'studentpage/home.html')  # 템플릿 경로 맞춰서
