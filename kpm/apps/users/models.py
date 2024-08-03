from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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
    name = models.CharField('user name', max_length=100)
    login = models.CharField('user login', max_length=20, unique=True)
    password = models.CharField('user password', max_length=200)
    experience = models.IntegerField('total student experience', default=0, null=True, blank=True)
    exam_experience = models.IntegerField('written exam student experience', default=0, null=True, blank=True)
    oral_exam_experience = models.IntegerField('oral exam student experience', default=0, null=True, blank=True)
    mana_earned = models.IntegerField('mana earned by student', default=0, null=True, blank=True)
    last_homework_id = models.IntegerField('last homework id', default=None, null=True, blank=True)
    last_classwork_id = models.IntegerField('last classwork id', default=None, null=True, blank=True)
    is_admin = models.BooleanField('is this account is admin', default=0)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    default_password = models.CharField('default password', max_length=5, null=True, blank=True)
    is_default = models.BooleanField('is default password', default=True)
    is_disabled = models.BooleanField('is user disabled', default=False)
    created_at = models.DateTimeField('user created at', auto_now_add=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name', 'default_password', 'is_admin']
    objects = UserManager()

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'users'


class History(models.Model):
    id = models.AutoField('id входа', primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField('Дата входа', auto_now_add=True)

    class Meta:
        db_table = 'history'


class Admin(models.Model):
    TIER_LIST = (
        (0, 'Стажер'),
        (1, 'Администратор'),
        (2, 'Супер-администратор'),
    )
    id = models.AutoField('id админа', primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    tier = models.IntegerField('Цвет группы', choices=TIER_LIST, default=0)

    class Meta:
        db_table = 'admins'