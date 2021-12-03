from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from coinanser.models import Question
from coinanser.upbit_quotation.get_rawdata import *
import json


def index(request):
    """
    question 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준

    # 정렬
    if so == 'recommend':
        question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:  # recent
        question_list = Question.objects.order_by('-create_date')

    # 조회
    # question_list = Question.objects.order_by('-create_date')
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(question_list, 5)  # 페이지당 5개씩 보여주기
    page_obj = paginator.get_page(page)
    page_len = paginator.num_pages
    page_start = max(1, page_obj.number - max(2, page_obj.number - page_len + 4))
    page_end = min(page_len, page_obj.number + max(2, 5 - page_obj.number))

    """
    rawdata 출력
    """
    gcm = get_candles_minutes('KRW-XRP')
    cr = candles_raw(gcm)

    # data_set = [
    #         [1, 37.8, 80.8, 41.8],
    #         [2, 30.9, 69.5, 32.4],
    #         [3, 25.4, 57, 25.7],
    #         [4, 11.7, 18.8, 10.5],
    #         [5, 11.9, 17.6, 10.4],
    #         [6, 11.9, 17.6, 100.4],
    #     ]
    data_set = [
        [
            d['date_time'],
            d['candle_acc_trade_price'] / d['candle_acc_trade_volume'],
            d['low_price'],
            d['high_price'],
        ] for d in cr]

    # data_set = [[datetime_convert(d['date_time'], to_str=False), d['date_time'], d['trade_price']] for i, d in enumerate(cr[:60])]

    context = {
        'question_list': page_obj,
        'question_list_len': page_len,
        'page_start': page_start,
        'page_end': page_end,
        'page': page,
        'kw': kw,
        'so': so,
        'data_set': data_set,
    }
    return render(request, 'coinanser/question_list.html', context)


def detail(request, question_id):
    """
    question 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'coinanser/question_detail.html', context)
