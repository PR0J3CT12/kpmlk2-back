from django.db import models
from kpm.apps.themes.models import Theme
from django.utils.deconstruct import deconstructible
import os
from kpm.apps.users.models import User
from django.core.exceptions import ValidationError
from .validators import validate_work_class_for_work_course
import uuid
from django.conf import settings
from minio import Minio
from django.utils.text import slugify
from minio.error import S3Error


STORAGE_PATH = settings.STORAGE_PATH
BUCKET_NAME = settings.STORAGES["default"]["OPTIONS"]["bucket_name"]
MINIO_ENDPOINT = settings.STORAGES["default"]["OPTIONS"]["endpoint_url"].replace("https://", "").replace("http://", "")
MINIO_ACCESS_KEY = settings.STORAGES["default"]["OPTIONS"]["access_key"]
MINIO_SECRET_KEY = settings.STORAGES["default"]["OPTIONS"]["secret_key"]
MINIO_USE_HTTPS = True
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_USE_HTTPS,
)

"""
@deconstructible
class PathRename(object):

    def __init__(self, sub_path):
        self.path = sub_path
        self.bucket_name = BUCKET_NAME

    def __call__(self, instance, filename):
        name, ext = os.path.splitext(filename)
        full_path = os.path.join(self.path, filename)
        media_full_path = f"media/{full_path}"

        if minio_client.bucket_exists(BUCKET_NAME):
            try:
                minio_client.stat_object(self.bucket_name, media_full_path)
                unique_id = str(uuid.uuid4())[:8]
                filename = f'{name}_{unique_id}{ext}'
                full_path = os.path.join(self.path, filename)
            except Exception:
                pass

        #if os.path.exists(os.path.join(STORAGE_PATH, full_path)):
        #    unique_id = str(uuid.uuid4())[:8]
        #    filename = f'{name}_{unique_id}{ext}'
        #    full_path = os.path.join(self.path, filename)
        return full_path
"""


@deconstructible
class PathRename:
    def __init__(self, sub_path):
        self.path = sub_path
        self.bucket_name = BUCKET_NAME

    def __call__(self, instance, filename):
        # Нормализуем имя файла
        name, ext = os.path.splitext(filename)

        # Формируем начальный путь для загрузки
        unique_filename = f"{name}{ext}"
        full_path = os.path.join(self.path, unique_filename)
        media_full_path = f"media/{full_path}"

        # Убедимся, что bucket существует
        # try:
        #     if not minio_client.bucket_exists(self.bucket_name):
        #         minio_client.make_bucket(self.bucket_name)
        # except S3Error as e:
        #     raise Exception(f"MinIO bucket error: {e}")

        while True:
            try:
                minio_client.stat_object(self.bucket_name, media_full_path)
                # Если файл существует, добавляем UUID
                unique_id = str(uuid.uuid4())[:8]
                unique_filename = f"{name}_{unique_id}{ext}"
                full_path = os.path.join(self.path, unique_filename)
                media_full_path = f"media/{full_path}"
            except S3Error as e:
                if e.code == "NoSuchKey":
                    # Файл не существует, можно загружать
                    break
                else:
                    raise Exception(f"MinIO error: {e}")

        return full_path


path_and_rename = PathRename("homeworks/service/")
path_and_rename_user = PathRename("homeworks/users/")


class Work(models.Model):
    TYPE_CHOICES = (
        (0, 'Домашняя работа'),
        (1, 'Классная работа'),
        (2, 'Блиц'),
        (3, 'Письменный экзамен классный'),
        (4, 'Устный экзамен классный'),
        (5, 'Письменный экзамен домашний'),
        (6, 'Устный экзамен домашний'),
        (7, 'Письменный экзамен домашний(баллы 2007)'),
        (8, 'Письменный экзамен классный(баллы 2007)'),
        (9, 'Вне статистики'),
        (10, 'Зачет'),
        (11, 'Проверка на рептилоида'),
    )
    COURSE_CHOICES = (
        (0, '4 класс'),
        (1, 'Продвинутый'),
        (2, 'Углубленный'),
        (3, 'Углубленный алгебра'),
        (4, 'Углубленный геометрия'),
        (5, 'Практикум'),
        (6, 'Алгебра'),
        (7, 'Геометрия'),
    )
    id = models.AutoField('work id', primary_key=True, editable=False)
    name = models.CharField('work name', max_length=100)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    school_class = models.IntegerField('student class', default=4)
    is_homework = models.BooleanField('is homework')
    type = models.IntegerField('work type', choices=TYPE_CHOICES, default=0)
    course = models.IntegerField('course', choices=COURSE_CHOICES)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='author', default=None, blank=True, null=True)

    # Grades fields
    grades = models.JSONField('work grades')
    max_score = models.FloatField('max score')
    exercises = models.IntegerField('amount of exercises')

    # Object fields
    has_attachments = models.BooleanField('has attachments', default=False)
    text = models.TextField('Текст домашней работы', default=None, null=True, blank=True)
    answers = models.JSONField('Форма с ответами', null=True, blank=True)
    is_closed = models.BooleanField('Работа закрыта', default=False)

    # Date fields
    created_at = models.DateTimeField('Дата создания работы', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления работы', auto_now_add=True)

    def clean(self):
        if self.school_class != self.theme.school_class:
            raise ValidationError(f"Работа {self.work.id} не соответствует классу темы '{self.theme.id}'.")
        if not validate_work_class_for_work_course(self.school_class, self.course):
            raise ValidationError(f"Курс работы не соответствует классу работы.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'works'


class Exam(models.Model):
    id = models.AutoField('link id', primary_key=True, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='work')
    work_2007 = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='work_2007')

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'exam_links'


class WorkFile(models.Model):
    id = models.AutoField('id файла', primary_key=True, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    file = models.FileField('Файл работы', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=100)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'works_files'


class WorkUser(models.Model):
    STATUS_CHOICES = (
        (0, 'Ожидает сдачи'),
        (1, 'Ожидает проверки'),
        (2, 'Проверена'),
        (3, 'Возвращена с комментарием'),
        (4, 'Просрочена'),
        (5, 'Просрочена и ожидает проверки'),
        (6, 'Просрочена и проверена'),
    )
    id = models.AutoField('id связи', primary_key=True, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField('Сдал ли работу ученик', default=False)
    comment = models.TextField('Комментарий преподавателя', default="", blank=True, null=True)
    is_checked = models.BooleanField('Проверена ли работа', default=False)
    checker = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='checker', null=True, blank=True, default=None)
    answers = models.JSONField('Форма с ответами')
    status = models.IntegerField('Статус работы', choices=STATUS_CHOICES, default=0)
    is_closed = models.BooleanField('Закрыта ли работа', default=False)

    answered_at = models.DateTimeField('Дата ответа', default=None, null=True, blank=True)
    checked_at = models.DateTimeField('Дата проверки', default=None, null=True, blank=True)
    added_at = models.DateTimeField('Дата выдачи работы', null=True, auto_now_add=True)

    def clean(self):
        if self.user.school_class != self.work.school_class:
            raise ValidationError(f"Ученик {self.user.id} не соответствует классу работы '{self.work.id}'.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'works_users'
        unique_together = ('work', 'user')


class WorkUserFile(models.Model):
    id = models.AutoField('id файла пользователя', primary_key=True, editable=False)
    link = models.ForeignKey(WorkUser, on_delete=models.CASCADE)
    file = models.FileField('Файл работы', upload_to=path_and_rename_user)
    ext = models.CharField('Расширение файла', max_length=100)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'works_users_files'
