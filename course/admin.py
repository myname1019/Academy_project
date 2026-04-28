from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',   
        'price',
        'video',
        'created_at'
    )

    list_filter = (
        'category',   
    )

    search_fields = (
        'title',     
    )