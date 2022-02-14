from django.shortcuts import render
# from coinanser.upbit_api.get_quotation import *
from datetime import datetime
from coinanser.upbit_api.get_quotation import MARKET_ALL
# from coinanser.upbit_api.get_quotation import get_candles_api
from coinanser.upbit_api.utils import datetime_convert, sig_fig5
from coinanser.data_handling.db_handler import get_upbit_quotation, get_db_rawdata
from coinanser.data_handling.rawdata_handler import refine_rawdata


def market_data(request):
    """
    upbit krw market list 및 rawdata 출력
    """
    market = request.GET.get('market')
    market_kw = request.GET.get('market_kw', '').lower()
    unit_get = request.GET.get('unit', 'days')
    endtime_get = request.GET.get('endtime', '')  # str
    show_count_get = request.GET.get('show_count')
    # market_all = get_market_all(print_=False)
    market_all = MARKET_ALL
    market_search = {k: market_all[k] for k in market_all
                     if market_kw in market_all[k]['korean_name']
                     or market_kw in market_all[k]['english_name'].lower()
                     or market_kw in market_all[k]['symbol'].lower()} if market_kw else market_all
    market_search = market_all if not market_search else market_search
    if market not in market_search:
        market = list(market_search.keys())[0]

    unit_list = [1, 5, 20, 60, 120, 'days', 'weeks', 'months']  # TODO: 구현 필요
    unit_str = {u: str(u) + ' 분' if type(u) == int else u for u in unit_list}
    unit_str['days'], unit_str['weeks'], unit_str['months'] = '일', '주', '월'
    unit = unit_get if unit_get in ['days', 'weeks', 'months'] else int(unit_get)

    show_count_list = [50, 100, 200]
    show_count_str = {sc: str(sc) + ' 건' if type(sc) == int else sc for sc in show_count_list}
    show_count = int(show_count_get) if show_count_get else 200

    time_now = datetime.now().strftime("%Y/%m/%d %H:%M")  # str
    endtime = min(time_now, endtime_get) if endtime_get else time_now  # str

    # gca = get_candles_api(market, unit_=unit,  # count_=show_count,
    #                       time_to_=datetime_convert(datetime.strptime(endtime, "%Y/%m/%d %H:%M"), sec_delta=60))
    # date_time_last = datetime_convert(gca[0]['date_time_last'], to_str=False).strftime("%Y/%m/%d %H:%M:%S")
    time_to = datetime_convert(datetime.strptime(endtime, "%Y/%m/%d %H:%M"), sec_delta=60)
    if unit in ['days', 'weeks', 'months']:
        rawdata = get_upbit_quotation(market, unit_=unit, time_to_=time_to)
    else:
        rawdata = get_db_rawdata(market, time_to_=time_to)
    refdata = refine_rawdata(rawdata)
    date_time_last = datetime_convert(refdata[0]['date_time_last'], to_str=False).strftime("%Y/%m/%d %H:%M:%S")
    print(date_time_last)

    # rev_gca = reversed(gca)
    # unit_price_list = []
    # for d in rev_gca:
    #     unit_price = {
    #         'date_time': d['date_time'],
    #         'high_price': d['high_price'],
    #         'low_price': d['low_price'],
    #         'trade_price_account': d['candle_acc_trade_price'],
    #         'mean_price': d['candle_acc_trade_price'] / d['candle_acc_trade_volume'] if d['candle_acc_trade_volume'] else unit_price_list[-1]['mean_price'],
    #     }
    #     unit_price['tooltip'] = (
    #             '거래시간: ' + datetime_convert(unit_price['date_time'], to_str=False).strftime("%Y/%m/%d %H:%M:%S") +
    #             '\\n고가: ' + format(sig_fig5(unit_price['high_price']), ',') + '원' +
    #             '\\n평균: ' + format(sig_fig5(unit_price['mean_price']), ',') + '원' +
    #             '\\n저가: ' + format(sig_fig5(unit_price['low_price']), ',') + '원' +
    #             '\\n거래금액: ' + format(round(unit_price['trade_price_account']), ',') + '원'
    #     )
    #     unit_price_list.append(unit_price)
    # unit_price_list.reverse()
    #
    # # if type(show_count) == int and len(gca) > show_count:
    # #     gca = gca[:show_count]
    # #     mean_price = mean_price[:show_count]
    # if type(show_count) == int and len(gca) > show_count:
    #     unit_price_list = unit_price_list[:show_count]

    ref_list = refdata[:show_count]
    for ref in refdata:
        ref['tooltip'] = (
                '거래시간: ' + datetime_convert(ref['date_time'], to_str=False).strftime("%Y/%m/%d %H:%M:%S") +
                '\\n고가: ' + format(sig_fig5(ref['high_price']), ',') + '원' +
                '\\n평균: ' + format(sig_fig5(ref['mean_price']), ',') + '원' +
                '\\n저가: ' + format(sig_fig5(ref['low_price']), ',') + '원' +
                '\\n거래금액: ' + format(round(ref['candle_acc_trade_price']), ',') + '원'
        )

    min_chart = min([r['low_price'] for r in ref_list])
    max_chart = max([r['high_price'] for r in ref_list])

    context = {
        # 'data_set': data_set,
        'market_kw': market_kw,
        'market_list': market_search,
        'market': market,
        'unit_str': unit_str,
        'unit': unit,
        'show_count_str': show_count_str,
        'show_count': show_count,
        'endtime': endtime,
        'date_time_last': date_time_last,
        'data_len': len(ref_list),
        'unit_price_list': ref_list,
        'min_chart': min_chart,
        'max_chart': max_chart,
    }
    return render(request, 'coinanser/market_chart.html', context)

