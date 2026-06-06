from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse

from .models import Project
from .forms import ProjectForm


def project_list(request):
    projects_qs = Project.objects.all().order_by('-created_at')

    paginator = Paginator(projects_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "projects": page_obj,
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_owner = request.user == project.owner
    is_participant = False

    if request.user.is_authenticated:
        is_participant = project.participants.filter(
            pk=request.user.pk).exists()

    return render(request, "projects/project-details.html", {
        "project": project,
        "is_owner": is_owner,
        "is_participant": is_participant,
    })


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
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False}
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
        {"form": form, "is_edit": True, "project": project}
    )


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.user == project.owner:
        return JsonResponse(
            {
                "status": "error",
                "error": "Автор не может менять статус участия"
            },
            status=403
        )

    if project.status != 'open':
        return JsonResponse(
            {
                "status": "error",
                "error": "Набор в проект завершен"
            },
            status=403
        )

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participating = False
    else:
        project.participants.add(request.user)
        is_participating = True

    return JsonResponse({
        "status": "ok",
        "participant": is_participating
    })


@login_required
def complete_project(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {
                "status": "error",
                "message": "Method not allowed"
            },
            status=405
        )

    project = get_object_or_404(Project, pk=pk)

    if project.owner == request.user and project.status == Project.Status.OPEN:
        project.status = Project.Status.CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})

    return JsonResponse(
        {
            "status": "error",
            "message": "Forbidden or project already closed"
        },
        status=403
    )
