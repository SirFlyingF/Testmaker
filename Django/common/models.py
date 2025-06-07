from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
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
    image = models.ImageField(upload_to='question-images', null=True, blank=True)
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

    module_choices = XRay_choices + MRI_choices

    title = models.CharField(max_length=256, blank=False, help_text="This will be displayed to the user")
    module = models.IntegerField(choices=module_choices) #Use FK for granularity
    file = models.FileField(upload_to='files', null=True)
    thumbnail = models.ImageField(upload_to='files', blank=True, null=True)

    def delete(self, *args, **kwargs):
        try:
            # Delete the files from S3 before deleting the model instance
            if self.file:
                self.file.delete(save=False)
            if self.thumbnail:
                self.thumbnail.delete(save=False)
        except Exception as e:
            print(f"[MediaFile] [delete()] {str(e)}")
        finally:
            super().delete(*args, **kwargs)

    class Meta:
        db_table = 'media_files'
        managed = True


class Product(models.Model):
    pass


class Payments(models.Model):
    STARTED = 1
    PENDING = 2
    COMPLETED = 3
    STATUS_CHOICES = (
        (STARTED, "Started"),
        (PENDING, "Pending"),
        (COMPLETED, "Completed")
    )

    product = models.ForeignKey(Product, on_delete=models.SET_NULL)
    token = models.TextField()
    amount = models.FloatField()
    status = models.IntegerField(choice=STATUS_CHOICES, default=STARTED)

    class Meta:
        db_table = "payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        managed = True


@receiver(pre_save, sender=MediaFile)
def generate_thumbnail(sender, instance, **kwargs):
    """Generate thumbnail for PDF files before saving the model instance"""
    try:
        if not instance.file:
            return
        
        if instance.pk:
            old_instance = MediaFile.objects.get(pk=instance.pk)
            if old_instance.file == instance.file:
                return
            else:
                # Delete files from S3 if it has been changed
                if old_instance.file:
                    old_instance.file.delete(save=False)
                if old_instance.thumbnail:
                    old_instance.thumbnail.delete(save=False)   

        fname, ftype = os.path.splitext(instance.file.name)
        if not ftype.lower() == '.pdf':
            instance.file = None
            return
        
        pdf = pypdfium2.PdfDocument(instance.file.file)
        pil_image = pdf.get_page(0).render(scale=1).to_pil()

        with BytesIO() as bytebuffer:
            pil_image.save(bytebuffer, 'PNG')
            bytebuffer.seek(0)
            instance.thumbnail.save(f"thumbnail_{fname}.png", ContentFile(bytebuffer.read()),save=False)

    except Exception as e:
        print(f"[MediaFile] [generate_thumbnail()] {str(e)}")
