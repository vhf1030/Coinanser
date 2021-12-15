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


# class RawData(models.Model):  # error - 테이블이 제대로 생성되지 않음 / 기존 DB를 복사하는 방식으로 진행해야 할 듯
#     date_time = models.DateTimeField(primary_key=True),
#     date_time_last = models.DateTimeField(null=True, blank=True),
#     opening_price = models.FloatField(null=True, blank=True),
#     high_price = models.FloatField(null=True, blank=True),
#     low_price = models.FloatField(null=True, blank=True),
#     trade_price = models.FloatField(null=True, blank=True),
#     candle_acc_trade_price = models.FloatField(null=True, blank=True),
#     candle_acc_trade_volume = models.FloatField(null=True, blank=True)

# 기존 db와 연동하는 경우:
# 1. python manage.py inspectdb 로 확인 및 복사하여 class 생성
# 2. python manage.py makemigrations
# 3. python manage.py migrate / 또는 python manage.py migrate --fake

class RawdataKrwAda(models.Model):
    date_time = models.DateTimeField(primary_key=True)  # primary_key가 db에 설정이 안되어있는 경우 직접 입력해야 함
    date_time_last = models.DateTimeField(blank=True, null=True)
    opening_price = models.FloatField(blank=True, null=True)
    high_price = models.FloatField(blank=True, null=True)
    low_price = models.FloatField(blank=True, null=True)
    trade_price = models.FloatField(blank=True, null=True)
    candle_acc_trade_price = models.FloatField(blank=True, null=True)
    candle_acc_trade_volume = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rawdata_krw-ada'



