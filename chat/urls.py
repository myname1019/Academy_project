from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("<int:course_id>/<int:other_user_id>/", views.dm_room, name="dm_room"),
]