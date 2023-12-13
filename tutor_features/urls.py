from django.urls import path
from .views import (
    mycourses,
    render_create_course_form,
    render_upload_material_form,
    show_submission,
    grade_submission,
)

urlpatterns = [
    path("create_course/", render_create_course_form, name="create_course"),
    path("mycourses/", mycourses, name="mycourses"),
    path("create_material/", render_upload_material_form, name="create_material"),
    path("showsubmissions/", show_submission, name="show_submission"),
]
