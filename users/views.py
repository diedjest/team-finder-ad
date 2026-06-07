import json
from http import HTTPStatus

from django.contrib.auth import (get_user_model, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

from .forms import UserLoginForm, UserProfileEditForm, UserRegisterForm
from .models import Skill

User = get_user_model()


def get_paginated_page(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def custom_logout(request):
    logout(request)
    return redirect(reverse_lazy("projects:project_list_alias"))


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"
    next_page = reverse_lazy("projects:project_list_alias")


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "users/register.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(reverse_lazy("projects:project_list_alias"))


@login_required
def my_profile(request):
    return render(
        request, "users/user-details.html", {"user": request.user, "is_owner": True}
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = UserProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


def user_detail(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    is_owner = request.user == profile_user
    return render(
        request, "users/user-details.html", {"user": profile_user, "is_owner": is_owner}
    )


def user_list(request):
    skill_filter = request.GET.get("skill")
    users_qs = User.objects.prefetch_related("skills").order_by("-id")
    all_skills = Skill.objects.all().order_by("name")

    active_skill_obj = None

    if skill_filter:
        users_qs = users_qs.filter(skills__name=skill_filter)
        active_skill_obj = all_skills.filter(name=skill_filter).first()

    page_obj = get_paginated_page(request, users_qs.distinct())

    return render(
        request,
        "users/participants.html",
        {
            "page_obj": page_obj,
            "participants": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill_obj,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def search_skills(request):
    query = request.GET.get("q", "").strip()
    if query:
        skills = Skill.objects.filter(name__istartswith=query).order_by("name")[:10]
        data = [{"id": skill.id, "name": skill.name} for skill in skills]
    else:
        data = []
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, pk):
    if request.user.pk != pk:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)

    data = json.loads(request.body)
    skill_id = data.get("skill_id")
    name = data.get("name")

    created = False
    added = False

    if skill_id:
        skill = Skill.objects.filter(id=skill_id).first()
        if not skill:
            return JsonResponse(
                {"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND
            )
    elif name:
        skill, created = Skill.objects.get_or_create(name=name.strip())
    else:
        return JsonResponse({"error": "No skill data"}, status=HTTPStatus.BAD_REQUEST)

    if not request.user.skills.filter(id=skill.id).exists():
        request.user.skills.add(skill)
        added = True

    return JsonResponse(
        {
            "skill_id": skill.id,
            "id": skill.id,
            "created": created,
            "added": added,
            "name": skill.name,
        }
    )


@login_required
@require_POST
def remove_skill(request, pk, skill_id):
    if request.user.pk != pk:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)

    skill = Skill.objects.filter(id=skill_id).first()
    if not skill:
        return JsonResponse({"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND)

    request.user.skills.remove(skill)
    return JsonResponse({"success": True})
