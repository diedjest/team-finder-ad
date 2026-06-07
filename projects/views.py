from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


def get_paginated_page(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def project_list(request):
    projects_qs = Project.objects.all().order_by("-created_at")
    page_obj = get_paginated_page(request, projects_qs)

    return render(
        request,
        "projects/project_list.html",
        {
            "page_obj": page_obj,
            "projects": page_obj,
        },
    )


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_owner = request.user == project.owner
    is_participant = False

    if request.user.is_authenticated:
        is_participant = project.participants.filter(pk=request.user.pk).exists()

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "is_owner": is_owner,
            "is_participant": is_participant,
        },
    )


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return HttpResponseForbidden("Вы не можете редактировать этот проект.")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@login_required
@require_POST
def toggle_participate(request, pk):
    project = Project.objects.filter(pk=pk).first()

    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )

    if request.user == project.owner:
        return JsonResponse(
            {"status": "error", "error": "Автор не может менять статус участия"},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != Project.Status.OPEN:
        return JsonResponse(
            {"status": "error", "error": "Набор в проект завершен"},
            status=HTTPStatus.FORBIDDEN,
        )

    is_participating = project.participants.filter(pk=request.user.pk).exists()

    if is_participating:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not is_participating})


@login_required
def complete_project(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Method not allowed"},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = Project.objects.filter(pk=pk).first()

    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )

    if project.owner == request.user and project.status == Project.Status.OPEN:
        project.status = Project.Status.CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": Project.Status.CLOSED})

    return JsonResponse(
        {"status": "error", "message": "Forbidden or project already closed"},
        status=HTTPStatus.FORBIDDEN,
    )
