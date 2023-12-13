from django import forms
from auth_app.views import Material, Course


class CreateCourseForm(forms.Form):
    title = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea)
    enrollment_capacity = forms.IntegerField()


class UploadMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["title", "content", "course", "document_type"]

        # initiate
        def __init__(self, tutor, *args, **kwargs):
            super(UploadMaterialForm, self).__init__(*args, **kwargs)
            # Limit the course choices to those created by the tutor
            self.fields["course"].queryset = Course.objects.filter(tutor=tutor)
