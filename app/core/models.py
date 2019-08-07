from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, \
                                   MinLengthValidator, MaxLengthValidator, \
                                   DecimalValidator, RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a new user"""
        if not phone_number:
            raise ValueError('User must have a phone_number')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, password):
        """Create and save a new superuser"""
        user = self.create_user(phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that support using phone number instead of username"""

    EDUCATION_CHOICES = [
        ('High school', 'High school'),
        ('College', 'College'),
        ('University', 'University')
    ]
    EMPLOYMENT_CHOICES = [
        ('Student', 'Student'),
        ('Full time', 'Full time'),
        ('Part time', 'Part time')
    ]
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. \
            Up to 15 digits allowed."
    )

    # INFO
    phone_number = models.CharField(_('phone number'), max_length=17,
                                    unique=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    name = models.CharField(max_length=255)
    first_name = models.CharField(_('first name'), max_length=30,
                                  blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30,
                                 blank=True, null=True)
    age = models.PositiveSmallIntegerField(_('age'),
                                           validators=[
                                                MinValueValidator(18),
                                                MaxValueValidator(150)
                                           ],
                                           blank=True, null=True)
    zipcode = models.PositiveSmallIntegerField(_('zipcode'),
                                               validators=[
                                                    MinLengthValidator(5),
                                                    MaxLengthValidator(5)
                                               ],
                                               blank=True, null=True)
    income = models.DecimalField(_('income'), max_digits=10, decimal_places=2,
                                 validators=[DecimalValidator], blank=True,
                                 null=True)
    education = models.CharField(_('education'), max_length=50,
                                 choices=EDUCATION_CHOICES, blank=True,
                                 null=True)
    employment = models.CharField(_('employment'), max_length=50,
                                  choices=EMPLOYMENT_CHOICES, blank=True,
                                  null=True)

    # SCORES
    scores_initial = models.ForeignKey('Score', on_delete=models.CASCADE,
                                       null=True, blank=True,
                                       related_name="score_initial_owner")
    scores_final = models.ForeignKey('Score', on_delete=models.CASCADE,
                                     null=True, blank=True,
                                     related_name="score_final_owner")

    date_joined = models.DateTimeField(_('registered'), auto_now_add=True,
                                       null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_full_name(self):
        """Returns the firstname plus the last_name, and a space in between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name


class Tag(models.Model):
    """Tags to be used for products"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


class Score(models.Model):
    """Score object"""
    MIN_SCORE = 0
    MAX_Score = 100

    version = models.CharField(max_length=5, blank=True, null=True)

    score_overall = models.PositiveSmallIntegerField(
                                           _('overall score'),
                                           validators=[
                                                MinValueValidator(MIN_SCORE),
                                                MaxValueValidator(MAX_Score)
                                           ],
                                           blank=True, null=True)
    score_medical = models.PositiveSmallIntegerField(
                                           _('medical score'),
                                           validators=[
                                                MinValueValidator(MIN_SCORE),
                                                MaxValueValidator(MAX_Score)
                                           ],
                                           blank=True, null=True)
    score_income = models.PositiveSmallIntegerField(
                                           _('income score'),
                                           validators=[
                                                MinValueValidator(MIN_SCORE),
                                                MaxValueValidator(MAX_Score)
                                           ],
                                           blank=True, null=True)
    score_stuff = models.PositiveSmallIntegerField(
                                           _('stuff you own score'),
                                           validators=[
                                                MinValueValidator(MIN_SCORE),
                                                MaxValueValidator(MAX_Score)
                                           ],
                                           blank=True, null=True)
    score_liability = models.PositiveSmallIntegerField(
                                           _('liabilities score'),
                                           validators=[
                                                MinValueValidator(MIN_SCORE),
                                                MaxValueValidator(MAX_Score)
                                           ],
                                           blank=True, null=True)
    score_digital = models.PositiveSmallIntegerField(
                                           _('digital score'),
                                           validators=[
                                                MinValueValidator(MIN_SCORE),
                                                MaxValueValidator(MAX_Score)
                                           ],
                                           blank=True, null=True)

    desc_overall = models.TextField(blank=True, null=True)
    desc_medical = models.TextField(blank=True, null=True)
    desc_income = models.TextField(blank=True, null=True)
    desc_stuff = models.TextField(blank=True, null=True)
    desc_liability = models.TextField(blank=True, null=True)
    desc_digital = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.score_overall)
