from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from django.contrib import messages
from rest_framework.response import Response
from django.shortcuts import render, redirect
from auth_app.models import User, Enrollment, Course, Assignment, Material, Grade
from auth_app.serializers import (
    EnrollmentSerializer,
    CourseSerializer,
    MaterialSerializer,
    GradeSerializer,
    SubmissionSerializer,
    InteractionHistorySerializer,
)
from rest_framework.decorators import api_view
from django.http import HttpResponse

from auth_app.views import signin


@api_view(["GET"])
def enroll_in_course(request, course_id):
    try:
        student = User.objects.get(email=request.user.email, role="STD")
        course = get_object_or_404(Course, pk=course_id)

        if Enrollment.objects.filter(student=student.pk, course=course.pk).exists():
            message = "Already enrolled"
            return render(request, "stddashboard.html", {"response": message})

        if (
            course.enrollment_capacity
            <= Enrollment.objects.filter(course_id=course.pk).count()
        ):
            message = "course at full capacity"
            return render(request, "stddashboard.html", {"response": message})
        enrollment = Enrollment.objects.create(student=student, course=course)
        # serializer = CourseSerializer(course)
        return render(request, "stddashboard.html")
    except User.DoesNotExist:
        return redirect(signin)


# view all courses
@api_view(["GET"])
def list_courses(request):
    courses = Course.objects.all()
    return render(request, "stddashboard.html", {"courses": courses})


@api_view(["GET"])
def enrolled_courses(request):
    try:
        student = User.objects.get(email=request.user.email, role="STD")
        enrolled_courses = Course.objects.filter(enrollment__student=student)
        materials = Material.objects.filter(course_id__in=enrolled_courses)

        context = {
            "courses": enrolled_courses,
            "materials": materials,
        }

        return render(request, "stddashboard.html", context)
    except User.DoesNotExist:
        return redirect(signin)


# @api_view(["GET"])
# def get_student_material(request):
#   try:
#      student = User.objects.get(email=request.user.email, role="STD")
#     joined_courses = Course.objects.filter(enrollment__student=student)
#    materials = Material.objects.filter(course__in=joined_courses)
# serializer = MaterialSerializer(materials, many=True)
#   return render(request, "student_material.html", {"materials": materials})


# except User.DoesNotExist:
#   return Response(
#      {"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND
# )


@api_view(["GET"])
def show_assign(request, assign_id):
    try:
        student = User.objects.get(email=request.user.email, role="STD")
        assignment = Assignment.objects.get(id=assign_id)
        course = Course.objects.get(course_id=assignment.course_id)
        context = {
            "assign": assignment,
            "course": course,
        }

        return render(request, "stddashboard_detail.html", {"detail": context})
    except User.DoesNotExist:
        return redirect(signin)
    except Assignment.DoesNotExist:
        return HttpResponse("Error: Assignment not found.")


def view_assignments(request):
    try:
        student = User.objects.get(email=request.user.email, role="STD")
        enrolled_courses = Course.objects.filter(enrollment__student=student)
        assignment = Assignment.objects.filter(course_id__in=enrolled_courses)

        return render(request, "stddashboard.html", {"assignments": assignment})
    except User.DoesNotExist:
        return redirect(signin)


@api_view(["POST"])
def save_interaction(request, action, course):
    try:
        student = User.objects.get(email=request.user.email, role="STD")
        data = {
            "interaction_type": action,
            "interaction_date": timezone.now(),
            "student_id": student.pk,
            "material_id": course,
        }
        serializer = InteractionHistorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Interaction saved successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def submit_work(request):
    try:
        if request.method == "POST":
            # Check if the required data is present in the request
            sub_content = request.data.get("sub_content")
            assignment_id = request.data.get("assignment_id")
            course = Assignment.objects.get(pk=assignment_id)
            # Get the student based on the user's email and role
            student = User.objects.get(email=request.user.email, role="STD")

            # Create the data dictionary for submission
            data = {
                "submission_content": sub_content,
                "submission_date": timezone.now(),
                "assignment": assignment_id,
                "student": student.pk,
            }

            # Validate and save the submission
            serializer = SubmissionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data = {
                "interaction_type": "assignment",
                "interaction_date": timezone.now(),
                "student_id": student.pk,
                "material_id": course.course_id,
                }
                serializer = InteractionHistorySerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                return redirect(view_assignments)

            else:
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def check_grades(request):
    try:
        student = User.objects.get(email=request.user.email, role="STD")
        grades = Grade.objects.filter(student_id=student)

        return render(request, "stddashboard.html", {"grades": grades})
    except User.DoesNotExist:
        return redirect("signin")  # Assuming 'signin' is the name of your sign-in view
    except Course.DoesNotExist:
        return HttpResponse("Error: No enrolled courses found.")


"""""
from rest_framework.decorators import api_view
from elearning_app.models import Course,Enrollment,User
from elearning_app.serializers import UserSerializer,CourseSerializer
from rest_framework.response import Response
from rest_framework import status
from admin_features.views import get_tutor_by_name



#view the courses of active Student 
@api_view(['GET'])
def enrolled_courses(request):
    try:
        student = Student.objects.get(email=request.user.email)
        enrolled_courses = student.courses_enrolled.all()
        if not enrolled_courses:
            return Response({'message': 'No courses yet'}, status=status.HTTP_200_OK)
        serializer = CourseSerializer(enrolled_courses, many=True)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    

#view all tutors
@api_view(['GET'])
def list_tutors(request):
    tutors = Tutor.objects.all()
    serializer = TutorSerializer(tutors, many=True)
    return Response(serializer.data)



#view courses by title
@api_view(['GET'])
def view_courses_by_title(request, title):
    try:
        courses_with_title = Course.objects.filter(title__iexact=title)
        if not courses_with_title:
            return Response({'message': f'No courses found with the title "{title}"'}, status=status.HTTP_200_OK)
        serializer = CourseSerializer(courses_with_title, many=True)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


#get course id
@api_view(['GET'])
def view_courses_by_tutor(request, tutor_name):
    try: 
        courses = Course.objects.filter(tutor__id=get_tutor_by_name['tutor_id']) #a tester ??
    except not courses:
        return Response({'message': f'No courses found by "{tutor_name}"'}, status=status.HTTP_200_OK)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def enroll_in_course(request, course_id):
    try:
        student = Student.objects.get(email=request.user.email)
        course = Course.objects.get(pk=course_id)

        if student.courses_enrolled.filter(pk=course_id).exists():
            return Response({'error': 'You are already enrolled in the course'}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = Enrollment.objects.create(student=student, course=course)
        serializer = CourseSerializer(enrollment.course)

        return Response({'message': f'Student enrolled in course "{enrollment.course.title}" successfully', 'course': serializer.data})
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
"""


""""
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    # Override create method to handle enrollment logic
    def create(self, request, *args, **kwargs):
        # You may want to customize this logic based on your requirements
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # Add other viewset methods as needed
"""
"""""
class CoursesViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        # Retrieve the user from the authentication token
        try:
            # Get the token from the request
            token_key = self.request.headers.get("Authorization").split(" ")[1]

            # Get the user associated with the token
            user = Token.objects.get(key=token_key).user

            # Filter the queryset to show only courses relevant to the user
            return Course.objects.filter(student=user)
        except Token.DoesNotExist:
            # Handle the case where the token is not found
            return Course.objects.none()

    # Add other viewset methods as needed


class GradesViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer

    def get_queryset(self):
        # Retrieve the user from the authentication token
        try:
            # Get the token from the request
            token_key = self.request.headers.get("Authorization").split(" ")[1]

            # Get the user associated with the token
            user = Token.objects.get(key=token_key).user

            # Filter the queryset to show only courses relevant to the user
            return Grade.objects.filter(students=user)
        except Token.DoesNotExist:
            # Handle the case where the token is not found
            return Grade.objects.none()


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        try:
            # Get the token from the request
            token_key = self.request.headers.get("Authorization").split(" ")[1]

            # Get the user associated with the token
            user = Token.objects.get(key=token_key).user

            # Filter assignments based on the courses the user has joined
            joined_courses = user.courses.all()
            related_assignments = Assignment.objects.filter(course__in=joined_courses)

            # Filter submissions based on the related assignments
            return Submission.objects.filter(assignment__in=related_assignments)
        except Token.DoesNotExist:
            return Submission.objects.none()

    # Override create method to handle enrollment logic
    def create(self, request, *args, **kwargs):
        # You may want to customize this logic based on your requirements
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # Add other viewset methods as needed


class HistoryViewSet(viewsets.ModelViewSet):
    serializer_class = InteractionHistorySerializer

    def get_queryset(self):
        # Retrieve the user from the authentication token
        try:
            # Get the token from the request
            token_key = self.request.headers.get("Authorization").split(" ")[1]

            # Get the user associated with the token
            user = Token.objects.get(key=token_key).user

            # Filter the queryset to show only courses relevant to the user
            return InteractionHistory.objects.filter(student=user)
        except Token.DoesNotExist:
            # Handle the case where the token is not found
            return InteractionHistory.objects.none()

"""
# save progress
