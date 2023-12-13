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
    UserTypes,
)
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class TutorSelectionForm(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return User.objects.filter(role=UserTypes.TUTOR)


class CourseSerializer(serializers.ModelSerializer):
    tutor = TutorSelectionForm(queryset=User.objects.filter(role=UserTypes.TUTOR))

    class Meta:
        model = Course
        fields = "__all__"


class StudentSelectionForm(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return User.objects.filter(role=UserTypes.STUDENT)


class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSelectionForm(queryset=User.objects.filter(role=UserTypes.STUDENT))

    class Meta:
        model = Enrollment
        fields = "__all__"


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = "__all__"


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"


class SubmissionSerializer(serializers.ModelSerializer):
    # student = StudentSelectionForm(queryset=User.objects.filter(role=UserTypes.STUDENT))

    class Meta:
        model = Submission
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["grade", "feedback", "assignment", "student"]


class InteractionHistorySerializer(serializers.ModelSerializer):
    student = StudentSelectionForm(queryset=User.objects.filter(role=UserTypes.STUDENT))

    class Meta:
        model = InteractionHistory
        fields = "__all__"


class ReadingStateSerializer(serializers.ModelSerializer):
    student = StudentSelectionForm(queryset=User.objects.filter(role=UserTypes.STUDENT))

    class Meta:
        model = ReadingState
        fields = "__all__"
