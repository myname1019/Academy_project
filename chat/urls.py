from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.inbox, name="inbox"),

    # 학생용: course_id만 받고, 항상 해당 강사와의 DM으로 이동(잠금)
    path("<int:course_id>/", views.dm_room_course, name="dm_room_course"),

    # 강사용: course_id + other_user_id(학생 id)로 DM 입장
    path("<int:course_id>/<int:other_user_id>/", views.dm_room, name="dm_room"),
]