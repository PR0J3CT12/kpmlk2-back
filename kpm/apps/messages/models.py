from django.db import models
from kpm.apps.users.models import User
from django.utils.deconstruct import deconstructible
import os


@deconstructible
class PathRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        return os.path.join(self.path, filename)


path_and_rename = PathRename("messages/")


class MessageGroup(models.Model):
    id = models.AutoField('group id', primary_key=True, editable=False)
    datetime = models.DateTimeField('group datetime', auto_now_add=True)

    class Meta:
        db_table = 'messages_groups'


class Message(models.Model):
    id = models.AutoField('message id', primary_key=True, editable=False)
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    text = models.TextField('message text')
    group = models.ForeignKey(MessageGroup, on_delete=models.CASCADE)
    is_viewed = models.BooleanField('has the message been read by the recipient', default=False)

    class Meta:
        db_table = 'messages'


class MessageGroupFile(models.Model):
    id = models.AutoField('message file id', primary_key=True, editable=False)
    message_group = models.ForeignKey(MessageGroup, on_delete=models.CASCADE)
    file = models.FileField('Файл работы', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=100)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'messages_group_files'