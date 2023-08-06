from django.db import models
from kpm.apps.users.models import User


class Message(models.Model):
    id = models.AutoField('message id', primary_key=True, editable=False)
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    text = models.TextField('message text')
    is_viewed = models.BooleanField('has the message been read by the recipient', default=False)
    datetime = models.DateTimeField('message datetime', auto_now_add=True)

    class Meta:
        db_table = 'messages'