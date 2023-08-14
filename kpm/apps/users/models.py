from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Group(models.Model):
    id = models.AutoField('group id', primary_key=True, editable=False)
    name = models.CharField('group name', max_length=100, unique=True)
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'groups'


class UserManager(BaseUserManager):
    def create_user(self, name, login, password, is_admin):
        if login is None:
            raise TypeError('Users must have a login.')
        if password is None:
            raise TypeError('Users must have a password.')

        user = self.model(login=login,
                          name=name,
                          is_admin=is_admin)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField('user id', primary_key=True, editable=False)
    name = models.CharField('user name', max_length=20)
    login = models.CharField('user login', max_length=20, unique=True)
    password = models.CharField('user password', max_length=200)
    experience = models.IntegerField('student experience', default=1, null=True, blank=True)
    mana_earned = models.IntegerField('mana earned by student', default=0, null=True, blank=True)
    last_homework_id = models.IntegerField('last homework id', default=1, null=True, blank=True)
    last_classwork_id = models.IntegerField('last classwork id', default=1, null=True, blank=True)
    is_admin = models.BooleanField('is this account is admin', default=0)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    default_password = models.CharField('default password', max_length=5, null=True, blank=True)
    is_default = models.BooleanField('is default password', default=True)
    group = models.ForeignKey(Group, default=None, null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name', 'default_password', 'is_admin']
    objects = UserManager()

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'users'