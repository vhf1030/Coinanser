from django.shortcuts import render
from coinanser.upbit_api.get_quotation import *


def market_data(request):
    """
    upbit krw market list 및 rawdata 출력
    """
    market = request.GET.get('market')
    market_kw = request.GET.get('market_kw', '').lower()
    unit_get = request.GET.get('unit', 'days')
    endtime_get = request.GET.get('endtime', '')  # str
    show_count_get = request.GET.get('show_count')
    market_all = get_market_all(print_=False)
    market_search = {k: market_all[k] for k in market_all
                     if market_kw in market_all[k]['korean_name']
                     or market_kw in market_all[k]['english_name'].lower()
                     or market_kw in market_all[k]['symbol'].lower()} if market_kw else market_all
    market_search = market_all if not market_search else market_search
    if market not in market_search:
        market = list(market_search.keys())[0]

    unit_list = [1, 3, 5, 10, 15, 30, 60, 240, 'days', 'weeks', 'months']
    unit_str = {u: str(u) + ' 분' if type(u) == int else u for u in unit_list}
    unit_str['days'], unit_str['weeks'], unit_str['months'] = '일', '주', '월'
    unit = unit_get if unit_get in ['days', 'weeks', 'months'] else int(unit_get)

    # show_count_list = [50, 100, 200, 'max']
    show_count_list = [50, 100, 200]
    show_count_str = {sc: str(sc) + ' 건' if type(sc) == int else sc for sc in show_count_list}
    # show_count_str['max'] = '최대'
    # show_count = show_count_get if show_count_get == 'max' else int(show_count_get)
    show_count = int(show_count_get) if show_count_get else 200

    # time_now = datetime.now().strftime("%Y/%m/%d %H:%M")
    # endtime_get = request.GET.get('endtime', time_now)
    # endtime = datetime.strptime(min(time_now, endtime_get), "%Y/%m/%d %H:%M")
    # # gcm = get_candles_minutes(market, min_=unit)
    # # cr = candles_raw(gcm, min_=unit)
    # gca = get_candles_api(market, unit_=unit, time_to_=endtime)

    # time_now = datetime.now().strftime("%Y/%m/%d %H:%M")  # str
    # endtime_get = request.GET.get('endtime', time_now)  # str
    # endtime = min(time_now, endtime_get)  # str

    time_now = datetime.now().strftime("%Y/%m/%d %H:%M")  # str
    endtime = min(time_now, endtime_get) if endtime_get else time_now  # str

    gca = get_candles_api(market, unit_=unit,  # count_=show_count,
                          time_to_=datetime_convert(datetime.strptime(endtime, "%Y/%m/%d %H:%M"), sec_delta=60))
    date_time_last = datetime_convert(gca[0]['date_time_last'], to_str=False).strftime("%Y/%m/%d %H:%M:%S")

    rev_gca = reversed(gca)
    mean_price, check = [], 1
    for d in rev_gca:
        if d['candle_acc_trade_volume'] == 0:  # 거래량이 0인 경우 평균가격 계산 에러
            mp = mean_price[-1]
        else:
            mp = d['candle_acc_trade_price'] / d['candle_acc_trade_volume']
        mean_price.append(mp)
    mean_price.reverse()
    # for d in gca:
    #     if d['candle_acc_trade_volume'] == 0:  # 거래량이 0인 경우 평균가격 계산 에러
    #         check += 1
    #     else:
    #         mp = [d['candle_acc_trade_price'] / d['candle_acc_trade_volume']]
    #         mean_price.extend(mp * check)
    #         check = 1
    if type(show_count) == int and len(gca) > show_count:
        gca = gca[:show_count]
        mean_price = mean_price[:show_count]

    context = {
        # 'data_set': data_set,
        'market_kw': market_kw,
        'market_list': market_search,
        'market': market,
        # 'unit_list': unit_list,
        'unit_str': unit_str,
        'unit': unit,
        'show_count_str': show_count_str,
        'show_count': show_count,
        'endtime': endtime,
        'date_time': [d['date_time'] for d in gca],
        'date_time_last': date_time_last,
        'high_price': [d['high_price'] for d in gca],
        'mean_price': mean_price,
        'low_price': [d['low_price'] for d in gca],
        'trade_price_account': [d['candle_acc_trade_price'] for d in gca],
        'data_len': len(gca),
    }
    return render(request, 'coinanser/market_chart.html', context)

