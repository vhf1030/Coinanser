from django.shortcuts import render
from datetime import datetime
from coinanser.upbit_api.get_quotation import MARKET_ALL
from coinanser.upbit_api.utils import datetime_convert, sig_fig5
from coinanser.data_handling.db_handler import get_atpu_seq, run_insert_product_DB


def atpu_board(request):
    """
    upbit krw market list 및 atpudata 출력
    """   # TODO: db에서 market list 가져오는 것으로 변경 필요
    market = request.GET.get('market')
    market_kw = request.GET.get('market_kw', '').lower()
    unit_get = request.GET.get('unit', '100')
    endtime_get = request.GET.get('endtime', '')  # str
    show_count_get = request.GET.get('show_count')
    market_all = MARKET_ALL
    market_search = {
        k: market_all[k] for k in market_all
        if market_kw in market_all[k]['korean_name']
           or market_kw in market_all[k]['english_name'].lower()
           or market_kw in market_all[k]['symbol'].lower()
    } if market_kw else market_all
    market_search = market_all if not market_search else market_search
    if market not in market_search:
        market = list(market_search.keys())[0]

    # unit_list = [1, 3, 5, 10, 15, 30, 60, 240, 'days', 'weeks', 'months']
    # unit_str = {u: str(u) + ' 분' if type(u) == int else u for u in unit_list}
    # unit_str['days'], unit_str['weeks'], unit_str['months'] = '일', '주', '월'
    # unit = unit_get if unit_get in ['days', 'weeks', 'months'] else int(unit_get)
    unit_list = [100]
    unit_str = {u: str(u) + ' 억원' for u in unit_list}
    unit = int(unit_get)

    show_count_list = [50, 100, 200]
    show_count_str = {sc: str(sc) + ' 건' if type(sc) == int else sc for sc in show_count_list}
    show_count = int(show_count_get) if show_count_get else 200

    time_now = datetime.now().strftime("%Y/%m/%d %H:%M")  # str
    endtime = min(time_now, endtime_get) if endtime_get else time_now  # str

    # gca = get_candles_api(market, unit_=unit,  # count_=show_count,
    #                       time_to_=datetime_convert(datetime.strptime(endtime, "%Y/%m/%d %H:%M"), sec_delta=60))
    # date_time_last = datetime_convert(gca[0]['date_time_last'], to_str=False).strftime("%Y/%m/%d %H:%M:%S")
    run_insert_product_DB(market, db='atpu')
    # TODO: 계산 중 페이지를 이동하는 경우 insert가 완전히 되지 않는 것으로 보임 - 확인 필요
    atpu_seq = get_atpu_seq(market, count_=show_count,
                            time_to_=datetime_convert(datetime.strptime(endtime, "%Y/%m/%d %H:%M"), sec_delta=60))
    date_time_first = datetime_convert(atpu_seq[-1]['s_date_time'], to_str=False).strftime("%Y/%m/%d %H:%M:%S")
    date_time_last = datetime_convert(atpu_seq[0]['s_date_time'], to_str=False,
                                      sec_delta=atpu_seq[0]['duration']).strftime("%Y/%m/%d %H:%M:%S")
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

    # if type(show_count) == int and len(gca) > show_count:
    #     unit_price_list = unit_price_list[:show_count]
    # min_chart = min([up['low_price'] for up in unit_price_list])
    # max_chart = max([up['high_price'] for up in unit_price_list])

    atpu_seq_list = atpu_seq[:show_count]
    atpu_seq_list.reverse()
    i = 0
    for atpu in atpu_seq_list:
        i += 1
        atpu['record'] = i
        atpu['e_date_time'] = datetime_convert(atpu['e_date_time'])
        atpu['s_date_time'] = datetime_convert(atpu['s_date_time'])
        atpu['tooltip'] = (
                '완료시간: ' + datetime_convert(atpu['e_date_time'], to_str=False).strftime("%Y/%m/%d %H:%M:%S") +
                '\\n시작시간: ' + datetime_convert(atpu['s_date_time'], to_str=False).strftime("%Y/%m/%d %H:%M:%S") +
                '\\n소요시간: ' + str(atpu['duration'] // 60) + '분 ' + str(atpu['duration'] % 60) + '초' +
                '\\n고가: ' + format(sig_fig5(atpu['high_price']), ',') + '원' +
                '\\n평균: ' + format(sig_fig5(atpu['mean_price']), ',') + '원' +
                '\\n저가: ' + format(sig_fig5(atpu['low_price']), ',') + '원' +
                '\\n거래금액: ' + format(round(atpu['atp_sum']), ',') + '원'
        )

    min_chart = min([atpu['low_price'] for atpu in atpu_seq_list])
    max_chart = max([atpu['high_price'] for atpu in atpu_seq_list])

    context = {
        'market_kw': market_kw,
        'market_list': market_search,
        'market': market,
        'unit_str': unit_str,
        'unit': unit,
        'show_count_str': show_count_str,
        'show_count': show_count,
        'endtime': endtime,
        'date_time_first': date_time_first,
        'date_time_last': date_time_last,
        'data_len': len(atpu_seq_list),
        'atpu_seq_list': atpu_seq_list,
        'min_chart': min_chart,
        'max_chart': max_chart,
    }
    return render(request, 'coinanser/account_price.html', context)

