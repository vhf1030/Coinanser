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


class TradeResults(models.Model):
    trade_id = models.CharField(primary_key=True, max_length=31)  # 첫 거래요청 id
    start_date_time = models.DateTimeField(db_index=True)  # 모델 예측 시각
    predict_model = models.CharField(max_length=31)  # 예측모델 이름
    model_version = models.FloatField()  # 모델 버전
    market = models.CharField(max_length=15)  # 마켓명
    bid_goal = models.FloatField()  # 목표 매수가격
    ask_goal = models.FloatField()  # 목표 매도가격
    # 매수 진행
    bid_date_time = models.DateTimeField(blank=True, null=True)  # 최종 매수시각  # 예측값이 변경된 경우 취소
    bid_price = models.FloatField(blank=True, null=True)  # 실제 매수가격  # 목표가와 다른 경우 실패처리
    bid_volume = models.FloatField(blank=True, null=True)  # 매수 수량
    bid_funds = models.FloatField(blank=True, null=True)  # 수수료 포함 매수금액
    # 매도 진행
    ask_date_time = models.DateTimeField(blank=True, null=True)  # 최종 매도시각  # 시장가 5000원 이하면 지정가 매도
    ask_price = models.FloatField(blank=True, null=True)  # 실제 매도가격  # 목표가와 다른 경우 실패처리
    ask_volume = models.FloatField(blank=True, null=True)  # 매도 수량
    ask_funds = models.FloatField(blank=True, null=True)  # 수수료 포함 매도금액
    # django를 통해 생성하는 경우 class Meta 가 없어야 함


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


# 기존 db 테이블 복사:
# 1. sql 실행
# (sql) CREATE TABLE test.`rawdata_krw-1inch` LIKE coinanser.`rawdata_krw-1inch`;
# (sql) INSERT INTO test.`rawdata_krw-1inch` SELECT * FROM coinanser.`rawdata_krw-1inch`;
# 2. table 생성
# python manage.py inspectdb, 복사 붙여넣기
# python manage.py makemigrations
# python manage.py migrate
class RawdataKrw1Inch(models.Model):
    date_time = models.DateTimeField(primary_key=True)
    date_time_last = models.DateTimeField(blank=True, null=True)
    opening_price = models.FloatField(blank=True, null=True)
    high_price = models.FloatField(blank=True, null=True)
    low_price = models.FloatField(blank=True, null=True)
    trade_price = models.FloatField(blank=True, null=True)
    candle_acc_trade_price = models.FloatField(blank=True, null=True)
    candle_acc_trade_volume = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rawdata_krw-1inch'


