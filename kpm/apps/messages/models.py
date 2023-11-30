from django.db import models
from kpm.apps.users.models import User


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