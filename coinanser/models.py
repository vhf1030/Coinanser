from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_question')  # 추천인 추가

    def __str__(self):
        return self.subject


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')

    def __str__(self):
        return self.content


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)


class RawData(models.Model):  # error - 테이블이 제대로 생성되지 않음
    date_time = models.DateTimeField(primary_key=True),
    date_time_last = models.DateTimeField(null=True, blank=True),
    opening_price = models.FloatField(null=True, blank=True),
    high_price = models.FloatField(null=True, blank=True),
    low_price = models.FloatField(null=True, blank=True),
    trade_price = models.FloatField(null=True, blank=True),
    candle_acc_trade_price = models.FloatField(null=True, blank=True),
    candle_acc_trade_volume = models.FloatField(null=True, blank=True)




