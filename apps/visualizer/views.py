from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation \
        import password_validators_help_text_html, validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User


@login_required
def index(request, id=None):
    return render(request, "visualizer/index.html")


def page_not_found(request, exception):
    return HttpResponseRedirect('/404')


def server_error(request):
    return HttpResponseRedirect('/500')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "visualizer/index.html", {
            "auth_fail_message": "Invalid username and/or password."
        })
    else:
        return render(request, "visualizer/index.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "visualizer/index.html", {
                "register_fail_message": "Passwords must match."
            })

        try:
            validate_password(password)
        except ValidationError:
            return render(request, "visualizer/index.html", {
                "register_fail_message": password_validators_help_text_html
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "visualizer/index.html", {
                "register_fail_message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "visualizer/index.html")
