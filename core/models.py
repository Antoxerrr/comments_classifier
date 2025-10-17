from django.db import models


class CommentData(models.Model):

    text = models.TextField("Текст комментария")
    is_toxic = models.BooleanField("Токсичный?")
    is_trusted = models.BooleanField("Доверенные данные", default=False)
