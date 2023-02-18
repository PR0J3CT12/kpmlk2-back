from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password, fullname, phone, role):
        if email is None:
            raise TypeError('Users must have an email address.')
        if password is None:
            raise TypeError('Users must have a password.')

        user = self.model(email=self.normalize_email(email),
                          fullname=fullname,
                          phone=phone,
                          role=role)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.IntegerField('user id', primary_key=True, editable=False)
    name = models.CharField('user name', max_length=20)
    login = models.CharField('user login', max_length=20, unique=True)
    password = models.CharField('user password', max_length=200, null=True, blank=True)
    experience = models.IntegerField('student experience', default=1, null=True, blank=True)
    mana_earned = models.IntegerField('mana earned by student', default=0, null=True, blank=True)
    last_homework_id = models.IntegerField('last homework id', default=1, null=True, blank=True)
    last_classwork_id = models.IntegerField('last classwork id', default=1, null=True, blank=True)
    is_admin = models.BooleanField('is this account is admin', default=0)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    default_password = models.CharField('default password', max_length=5, null=True, blank=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name', 'default_password', 'is_admin']
    objects = UserManager()

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'users'
