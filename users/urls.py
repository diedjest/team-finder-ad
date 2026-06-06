from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.custom_logout, name="logout"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("profile/", views.my_profile, name="my_profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("<int:pk>/", views.user_detail, name="user_detail"),
    path("list/", views.user_list, name="user_list"),
    path("change-password/", views.change_password, name="change_password"),
    path("skills/", views.search_skills, name="search_skills"),
    path("skills", views.search_skills),
    path("<int:pk>/skills/add/", views.add_skill, name="add_skill"),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.remove_skill,
        name="remove_skill"
    ),
]
