# urls.py
from django.urls import path
from .views import (
    enroll_in_course,
    list_courses,
    enrolled_courses,
    check_grades,
    view_assignments,
    show_assign,
    submit_work,
    save_interaction,
)

urlpatterns = [
    # path('student_material/', get_student_material, name='student_material'),
    path("enroll/<int:course_id>/", enroll_in_course, name="enroll_in_course"),
    path("list_courses/", list_courses, name="list_courses"),
    path("student_courses/", enrolled_courses, name="student_courses"),
    path("grades/", check_grades, name="grades"),
    path("assignments/", view_assignments, name="assignments"),
    path("assignments/<int:assign_id>", show_assign, name="show_assign"),
    path("assignments/submit_work", submit_work, name="submit_work"),
    path(
        "save_interaction/<str:action>/<str:course>/",
        save_interaction,
        name="save_interaction",
    ),
]
