from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserTypes(models.TextChoices):
    STUDENT = "STD", "Student"
    TUTOR = "TUT", "Tutor"
    ADMIN = "ADM", "Admin"


class DocTypes(models.TextChoices):
    PDF = "PDF", "Pdf"
    DOC = "DOC", "Microsoft Word"
    PPT = "PPT", "Microsoft PowerPoint"
    TEXT = "TXT", "Text"
    HTML = "HTML", "Html"
    JPEG_IMAGE = "JPEG", "JPEG Image"
    PNG_IMAGE = "PNG", "PNG Image"
    ZIP = "ZIP", "Zip"


# user input controler
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
    role = models.CharField(
        max_length=4, choices=UserTypes.choices, default=UserTypes.STUDENT
    )
    datejoined = models.DateField(auto_now_add=True)

    # Add any additional fields as needed

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "role"]

    class Meta:
        db_table = "users"
        ordering = ["role"]

    def __str__(self):
        return f"username={self.username}, email={self.email}, date joined={self.datejoined}"


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    tutor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courses_teaching"
    )
    # tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE) # tutor class passed as string beacuse it's not defined yet
    enrollment_capacity = models.PositiveIntegerField()

    class Meta:
        db_table = "course"
        ordering = ["title"]

    def __str__(self):
        return f"title={self.title}/enrollment_capacity={self.enrollment_capacity}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    # student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "enrollment"
        unique_together = ["student", "course"]


class Material(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="materials"
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(
        max_length=20, choices=DocTypes.choices, default=DocTypes.DOC
    )

    class Meta:
        db_table = "material"


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    due_date = models.DateTimeField()

    class Meta:
        db_table = "assignment"


class Submission(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="submissions"
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submission_content = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "submission"


class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="grades")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField()

    class Meta:
        db_table = "grade"


class InteractionHistory(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="interactions"
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50)
    interaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interaction_history"


class ReadingState(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reading_states"
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    read_state = models.IntegerField()
    last_read_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reading_state"
