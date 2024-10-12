from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from io import BytesIO
import pypdfium2, os


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.is_active = extra_fields.get('is_active', False)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.display_name} - {self.email} - {'Staff' if self.is_staff else 'Student'}"
    
    class Meta:
        db_table = 'user'
        managed = True


class Chapter(models.Model):
    PATIENT_CARE = 11
    SAFETY = 12
    IMAGE_PRODUCTION = 13
    PROCEDURES = 14
    XRay_choices = [
        (PATIENT_CARE, 'Patient Care'),
        (SAFETY, 'Safety'),
        (IMAGE_PRODUCTION, 'Image Production'),
        (PROCEDURES, 'Procedures')
    ]

    PHYSICS = 21
    BIOLOGY = 22
    CONTRAST_MEDIA = 23
    PATHOLOGY = 24
    MRI_choices = [
        (PHYSICS, 'Radiologic Physics'),
        (BIOLOGY, 'Radiation Biology'),
        (CONTRAST_MEDIA, 'Contrast Media'),
        (PATHOLOGY, 'Pathology')
    ]

    chapter_choices = XRay_choices + MRI_choices

    name = models.CharField(max_length=64)
    module = models.IntegerField(choices=chapter_choices)

    class Meta:
        db_table = 'chapter'
        managed = True


class Question(models.Model):
    MCQ = 1
    MSQ = 2
    TFQ = 3
    type_choices = [
        (MCQ, 'Multiple Choice Question'),
        (MSQ, 'Multiple Select Question'),
        (TFQ, 'True or False')
    ]

    text = models.TextField()
    type = models.IntegerField(choices=type_choices, default=MCQ)
    option_a = models.CharField(max_length=128)
    option_b = models.CharField(max_length=128)
    option_c = models.CharField(max_length=128, null=True, blank=True)
    option_d = models.CharField(max_length=128, null=True, blank=True)
    answer_key = models.CharField(max_length=4)
    # image = models.ImageField(upload_to='')
    chapter = models.ForeignKey('Chapter', on_delete=models.DO_NOTHING, db_constraint=False)
    obsolete_ind = models.BooleanField(default=False)
    created_dt_tm = models.DateTimeField(auto_now_add=True)
    updt_dt_tm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question'
        managed = True


class Test(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField(max_length=64)
    start_dt_tm = models.DateTimeField(null=True)
    end_dt_tm = models.DateTimeField(null=True)
    score = models.FloatField(null=True)
    updt_dt_tm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test'
        managed = True


class QuestionTest(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, db_constraint=False)
    test = models.ForeignKey('Test', on_delete=models.CASCADE, db_constraint=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_constraint=False)
    answer = models.BooleanField(default=None, null=True)
    elapsed_time = models.DurationField(null=True)

    class Meta:
        db_table = 'question_test_reltn'
        managed = True


class MediaFile(models.Model):
    PATIENT_CARE = 11
    SAFETY = 12
    IMAGE_PRODUCTION = 13
    PROCEDURES = 14
    XRay_choices = [
        (PATIENT_CARE, 'Patient Care'),
        (SAFETY, 'Safety'),
        (IMAGE_PRODUCTION, 'Image Production'),
        (PROCEDURES, 'Procedures')
    ]

    PHYSICS = 21
    BIOLOGY = 22
    CONTRAST_MEDIA = 23
    PATHOLOGY = 24
    MRI_choices = [
        (PHYSICS, 'Radiologic Physics'),
        (BIOLOGY, 'Radiation Biology'),
        (CONTRAST_MEDIA, 'Contrast Media'),
        (PATHOLOGY, 'Pathology')
    ]

    chapter_choices = XRay_choices + MRI_choices

    title = models.CharField(max_length=256, blank=False, help_text="This will be displayed to the user")
    module = models.IntegerField(choices=chapter_choices) #Use FK for granularity
    file = models.FileField(upload_to='files')
    thumbnail = models.ImageField(upload_to='files', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate a thumbnail from uploaded pdf
        if self.file:
            try:
                fname, ftype = os.path.splitext(self.file.name)
                if not ftype.lower() == '.pdf':
                    raise TypeError('Unsupported Filetype')
                
                pdf = pypdfium2.PdfDocument(self.file.file)
                print('1 - got pdf')
                pil_image = pdf.get_page(0).render(scale=1).to_pil()
                print('2 - got img')

                bytebuffer = BytesIO()
                print('3 - got bytebuff')
                pil_image.save(bytebuffer, 'PNG')
                print('4 - image to bytebuff')
                bytebuffer.seek(0)
                self.thumbnail.save(f'thumbnail_{fname}.png', ContentFile(bytebuffer.read()), save=False)
                print('5 - saved thumbnail')
            except Exception as e:
                print(str(e) + f'{fname}, {True if pil_image else False} - {True if self.file.file else False}')
                pass
            finally:
                bytebuffer.close()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'media_files'
        managed = True
