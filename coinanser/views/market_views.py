from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from coinanser.models import Question
from coinanser.upbit_quotation.get_rawdata import *
import json


def market_data(request):
    """
    upbit krw market list 및 rawdata 출력
    """
    unit_list = [1, 3, 5, 15, 10, 30, 60, 240]
    unit = int(request.GET.get('unit', 1))
    market = request.GET.get('market', 'KRW-BTC')
    market_all = get_market_all(print_=False)
    gcm = get_candles_minutes(market, min_=unit)
    cr = candles_raw(gcm, min_=unit)

    mean_price, check = [], 1
    for d in cr:
        if d['candle_acc_trade_volume'] == 0:  # 거래량이 0인 경우 평균가격 계산 에러
            check += 1
        else:
            mp = [d['candle_acc_trade_price'] / d['candle_acc_trade_volume']]
            mean_price.extend(mp * check)
            check = 1

    context = {
        # 'data_set': data_set,
        'unit_list': unit_list,
        'unit': unit,
        'market_list': market_all,
        'market': market,
        'date_time': [d['date_time'] for d in cr],
        'mean_price': mean_price,
        'trade_price': [d['candle_acc_trade_price'] for d in cr],
        'data_len': len(cr),
    }
    return render(request, 'coinanser/market_chart.html', context)

