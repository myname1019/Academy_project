from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# 1. 방금 만든 Student, Teacher 모델도 함께 불러오도록 수정합니다.
from .models import CustomUser, Student, Teacher 

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# 2. 🚀 관리자 페이지에 학생과 선생님 테이블 메뉴를 띄우도록 최종 등록!
admin.site.register(Student)
admin.site.register(Teacher)