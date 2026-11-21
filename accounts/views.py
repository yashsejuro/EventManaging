"""Small account views; Django provides the login/logout implementation."""

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import SignupForm


@require_http_methods(["GET", "POST"])
def signup(request):
    """Create a built-in User with UserCreationForm and sign them in."""
    if request.user.is_authenticated:
        return redirect("events:home")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to ClubEvents!")
        return redirect("events:home")
    return render(request, "accounts/signup.html", {"form": form})
