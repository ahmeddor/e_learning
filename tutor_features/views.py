from rest_framework.response import Response
from rest_framework import status
from auth_app.serializers import CourseSerializer, MaterialSerializer, GradeSerializer
from django.contrib import messages
from auth_app.models import Course, User, Assignment, Submission
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from auth_app.views import signin
import logging
from .forms import CreateCourseForm, UploadMaterialForm


@api_view(["POST"])
def grade_submission(request):
    try:
        tutor = User.objects.get(email=request.user.email, role="TUT")

        if request.method == "POST":
            grade = request.data.get("grade")
            feedback = request.data.get("feedback")
            assign_id = request.data.get("assignment_id")
            student_id = request.data.get("student_id")

            data = {
                "grade": grade,
                "feedback": feedback,
                "assignment": assign_id,
                "student": student_id,
            }

            serializer = GradeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"response": "Successfully graded"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


def show_submission(request):
    try:
        if request.method == "POST":
            grade_submission(request)

        tutor = User.objects.get(email=request.user.email, role="TUT")
        courses = Course.objects.filter(tutor_id=tutor)
        assingment = Assignment.objects.filter(course_id__in=courses)
        submissions = Submission.objects.filter(assignment__in=assingment)
        return render(request, "tutrdshbrd.html", {"submissions": submissions})

    except User.DoesNotExist:
        return redirect(signin)


@api_view(["POST"])
def create_course(request):
    try:
        tutor = User.objects.get(email=request.user.email)
        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "enrollment_capacity": request.data.get("enrollment_capacity"),
            "tutor": tutor.pk,  # Set the tutor field to the ID of the active tutor
        }
        serializer = CourseSerializer(data=data)
        # insertion
        if serializer.is_valid():
            serializer.save()
            messages.success(
                request, f"Course '{serializer.data['title']}' added successfully."
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)


def render_create_course_form(request):
    try:
        # logging.info(f"User role: {request.user.role}")
        Tutor = User.objects.get(email=request.user.email, role="TUT")
        if request.method == "POST":
            form = CreateCourseForm(request.POST)
            if form.is_valid():
                # Handle form submission logic
                create_course(request)
                messages.success(
                    request,
                    f"Course '{form.cleaned_data['title']}' added successfully.",
                )
                return redirect(mycourses)
        else:
            form = CreateCourseForm()

        return render(request, "tutor_add_course.html", {"form": form})
    except User.DoesNotExist:
        return redirect(signin)


# view the courses of active tutor
@api_view(["GET"])
def mycourses(request):
    try:
        courses = Course.objects.filter(tutor=request.user.id)
        serializer = CourseSerializer(courses, many=True)
        return render(request, "tutrdshbrd.html", {"courses": serializer.data})
    except Course.DoesNotExist:
        return Response(
            {"error": "No courses found for the active tutor"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def upload_material(request):
    try:
        tutor = User.objects.get(email=request.user.email)
        data = {
            "title": request.data.get("title"),
            "content": request.data.get("content"),
            "course": request.data.get(
                "course_id"
            ),  # Assuming you pass the course_id in the request data
            "document_type": request.data.get(
                "document_type", "DOC"
            ),  # Default to DOC if not provided
        }
        serializer = MaterialSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)


def render_upload_material_form(request):
    try:
        Tutor = User.objects.get(email=request.user.email, role="TUT")
        if request.method == "POST":
            form = UploadMaterialForm(Tutor, request.POST)
            if form.is_valid():
                # Handle form submission logic
                upload_material(request)
                messages.success(
                    request,
                    f"Course '{form.cleaned_data['title']}' added successfully.",
                )
                return redirect(mycourses)
        else:
            form = UploadMaterialForm()

        return render(request, "tutor_add_material.html", {"form": form})
    except User.DoesNotExist:
        return redirect(signin)


""""
@api_view(['GET'])
def list_tutors(request):
    tutors = Tutor.objects.all()
    serializer = TutorSerializer(tutors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_tutor_by_id(request, tutor_id):
    try:
        tutor = Tutor.objects.get(pk=tutor_id)
    except Tutor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TutorSerializer(tutor)
    return Response(serializer.data)


    


#List all my students
@api_view(['GET'])
def tutor_students(request):
    try:
        # Get the courses of the active tutor
        tutor_courses = Tutor.objects.get(email=request.user.email).courses_tutored.all()
        
        # Get the students enrolled in those courses
        students = Student.objects.filter(courses_enrolled__in=tutor_courses)
        
        # Serialize the students
        serializer = StudentSerializer(students, many=True)
        
        return Response(serializer.data)
    except Tutor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

#list my students by course     
@api_view(['GET'])
def tutor_students_by_course(request):
    try:
        # Get the active tutor
        tutor = Tutor.objects.get(email=request.user.email)

        # Get the courses taught by the tutor
        tutor_courses = tutor.courses_tutored.all()

        #dict to store course and corresponding students
        students_by_course = {}

        # Iterate through each course and retrieve students
        for course in tutor_courses:
            students = Student.objects.filter(courses_enrolled=course)
            serialized_students = StudentSerializer(students, many=True).data
            students_by_course[course.title] = serialized_students

        return Response(students_by_course)
    except Tutor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    


 #return example : 

 {
    'Math 101': [
        {'user_id': 1, 'username': 'student1', 'email': 'student1@example.com', 'role': 'STD', 'datejoined': '2023-01-01', 'firstname': 'John', 'lastname': 'Doe'},
        {'user_id': 2, 'username': 'student2', 'email': 'student2@example.com', 'role': 'STD', 'datejoined': '2023-02-01', 'firstname': 'Jane', 'lastname': 'Doe'}
    ],
    'Physics 202': [
        {'user_id': 3, 'username': 'student3', 'email': 'student3@example.com', 'role': 'STD', 'datejoined': '2023-03-01', 'firstname': 'Alice', 'lastname': 'Smith'},
        {'user_id': 4, 'username': 'student4', 'email': 'student4@example.com', 'role': 'STD', 'datejoined': '2023-04-01', 'firstname': 'Bob', 'lastname': 'Johnson'}
    ],
    # ... more courses and their corresponding students
}


"""
