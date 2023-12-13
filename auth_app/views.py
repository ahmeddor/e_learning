from rest_framework import viewsets

# user_authentification/views.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import SignupForm, SignInForm
from django.contrib import messages

from .models import (
    User,
    Course,
    Enrollment,
    Material,
    Assignment,
    Submission,
    Grade,
    InteractionHistory,
    ReadingState,
)
from .serializers import (
    UserSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    MaterialSerializer,
    AssignmentSerializer,
    SubmissionSerializer,
    GradeSerializer,
    InteractionHistorySerializer,
    ReadingStateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class InteractionHistoryViewSet(viewsets.ModelViewSet):
    queryset = InteractionHistory.objects.all()
    serializer_class = InteractionHistorySerializer


class ReadingStateViewSet(viewsets.ModelViewSet):
    queryset = ReadingState.objects.all()
    serializer_class = ReadingStateSerializer


## view login signup


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("signin")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def signin(request):
    if request.method == "POST":
        form = SignInForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect(
                    "stddashboard.html"
                )  # Redirect to your dashboard or home page
                # return redirect('/tutor_features/create_course/')  # Redirect to your dashboard or home page
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = SignInForm()

    return render(request, "signin.html", {"form": form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("signin")  # Redirect to your signin page
