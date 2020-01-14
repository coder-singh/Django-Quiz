from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

class Role(models.Model):
    name = models.CharField(max_length=10, db_column='name')

    class Meta:
        db_table='Role'

class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('first_name', '')
        extra_fields.setdefault('last_name', '')
        extra_fields.setdefault('role', 1)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    first_name = models.CharField(db_column='first_name', max_length=20, blank=True, null=True)
    last_name = models.CharField(db_column='last_name', max_length=20, blank=True, null=True)
    role = models.IntegerField(db_column='role_id', blank=True, null=True)

    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.first_name

    def get_short_name(self):
        return self.first_name

class Quiz(models.Model):
    name = models.CharField(max_length=20, db_column='Name')
    time = models.IntegerField(db_column='Time', blank=True, null=True)
    tutor_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='Tutor_Id')
    max_marks = models.IntegerField(db_column='Max_Marks')
    pass_marks = models.IntegerField(db_column='Passing_Marks')
    no_questions = models.IntegerField(db_column='Number_Questions')

    class Meta:
        db_table = 'Quiz'

class QuestionType(models.Model):
    name = models.CharField(max_length=20, db_column='Name')

    class Meta:
        db_table = 'Question_Type'

class Question(models.Model):
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE, db_column='Quiz_Id', blank=True, null=True)
    q_text = models.CharField(max_length=100, db_column='Question_Text', blank=True, null=True)
    q_image = models.ImageField(upload_to='images/question/', db_column='Question_Image', blank=True, null=True) 
    q_video = models.CharField(max_length=100, db_column='Question_Video', blank=True, null=True)
    q_type = models.IntegerField(db_column='Question_Type', blank=True, null=True)
    a_text = models.CharField(max_length=100, db_column='Option1_Text', blank=True, null=True)
    a_image = models.ImageField(upload_to='images/option/', db_column='Option1_Image', blank=True, null=True) 
    a_video = models.CharField(max_length=100, db_column='Option1_Video', blank=True, null=True)
    b_text = models.CharField(max_length=100, db_column='Option2_Text', blank=True, null=True)
    b_image = models.ImageField(upload_to='images/option/', db_column='Option2_Image', blank=True, null=True) 
    b_video = models.CharField(max_length=100, db_column='Option2_Video', blank=True, null=True)
    c_text = models.CharField(max_length=100, db_column='Option3_Text', blank=True, null=True)
    c_image = models.ImageField(upload_to='images/option/', db_column='Option3_Image', blank=True, null=True) 
    c_video = models.CharField(max_length=100, db_column='Option3_Video', blank=True, null=True)
    d_text = models.CharField(max_length=100, db_column='Option4_Text', blank=True, null=True)
    d_image = models.ImageField(upload_to='images/option/', db_column='Option4_Image', blank=True, null=True) 
    d_video = models.CharField(max_length=100, db_column='Option4_Video', blank=True, null=True)
    answer = models.CharField(max_length=20, db_column='Answer', blank=True, null=True)

    class Meta:
        db_table = 'Question'
