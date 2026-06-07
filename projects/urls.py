from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "projects"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            pattern_name="projects:project_list_alias", permanent=False
        ),
        name="index_redirect",
    ),
    path("projects/list/", views.project_list, name="project_list_alias"),
    path("projects/create-project/", views.create_project, name="create_project"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", views.edit_project, name="edit_project"),
    path(
        "projects/<int:pk>/toggle-participate/",
        views.toggle_participate,
        name="toggle_participate",
    ),
    path(
        "projects/<int:pk>/complete/", views.complete_project, name="complete_project"
    ),
]
