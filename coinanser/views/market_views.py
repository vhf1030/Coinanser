from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from coinanser.models import Question
from coinanser.upbit_quotation.get_rawdata import *
import json


def market_data(request):
    """
    upbit market rawdata 출력
    """
    gcm = get_candles_minutes('KRW-XRP')
    cr = candles_raw(gcm)

    data_set = [
        [
            d['date_time'],
            d['candle_acc_trade_price'] / d['candle_acc_trade_volume'],
            d['low_price'],
            d['high_price'],
        ] for d in cr]

    # data_set = [[datetime_convert(d['date_time'], to_str=False), d['date_time'], d['trade_price']] for i, d in enumerate(cr[:60])]

    context = {
        'data_set': data_set,
        'date_time': [d['date_time'] for d in cr],
        'mean_price': [d['candle_acc_trade_price'] / d['candle_acc_trade_volume'] for d in cr],
        'trade_price': [d['candle_acc_trade_price'] for d in cr],
        'data_len': len(cr),
    }
    return render(request, 'coinanser/market_chart.html', context)

