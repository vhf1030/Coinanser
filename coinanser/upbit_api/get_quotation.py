import requests
from coinanser.upbit_api.utils import *
from time import sleep
from pprint import pprint


# Get data
# https://docs.upbit.com/reference/
def get_market_all(krw=True, print_=True):
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails": "true"}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, params=querystring, headers=headers)
    market_dict = {j['market']: j for j in response.json()}
    for md in list(market_dict.keys()):
        market_tmp = market_dict[md].pop('market').split("-")
        if krw and market_tmp[0] != 'KRW':
            market_dict.pop(md)
            continue
        market_dict[md]['symbol'] = market_tmp[1]
    if print_:
        print('market 수:', len(market_dict))
        print('markets:', ', '.join([market_dict[market]['korean_name'] for market in market_dict]))
    return market_dict


MARKET_ALL = get_market_all()
# pprint(MARKET_ALL)


# def get_candles_minutes(market_, time_to_=False, min_=1, count_=200, sleep_=0.1):
#     url = "https://api.upbit.com/v1/candles/minutes/" + str(min_)
#     to = datetime_convert(time_to_, to_str=False, to_utc=True) if time_to_ else ""
#     querystring = {"market": market_, "to": to, "count": str(count_)}
#     headers = {"Accept": "application/json"}
#     if sleep_:
#         sleep(sleep_)
#     response = requests.request("GET", url, headers=headers, params=querystring)
#     return response.json()
# # get_candles_minutes('KRW-BTC', count_=1)
# # get_candles_minutes('KRW-BTC', time_to_='2021-09-30T15:39:00', count_=1)  # 15:38:00 ~ 15:39:00
# # get_candles_minutes('KRW-BTC', time_to_='2021-09-30T15:39:01', count_=1)  # 15:39:00 ~ 15:40:00
#
#
# def candles_raw(gcm_, to_time_=False, reverse_=True, min_=1):
#     cr_list = []
#     from_time = gcm_[-1]['candle_date_time_kst']
#     to_time = gcm_[0]['candle_date_time_kst'] if not to_time_ else datetime_convert(to_time_, sec_delta=-60)
#     check_time = from_time  # 먼 시점부터 현재 시점으로 진행: 입력시간이 -1번 인덱스에 저장(gcm과 순서가 반대)
#     cm_dict = {cm['candle_date_time_kst']: cm for cm in gcm_}
#     remain_key_list = ['opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_price', 'candle_acc_trade_volume']
#     while check_time <= to_time:
#         cr_tmp = {}
#         if check_time in cm_dict:
#             cr_tmp['date_time'] = check_time
#             date_time_last = datetime_convert(cm_dict[check_time]['timestamp'])
#             cr_tmp['date_time_last'] = date_time_last
#             for rk in remain_key_list:
#                 cr_tmp[rk] = cm_dict[check_time][rk]
#             price = cr_tmp['trade_price']
#         else:  # 누락 시간 생성
#             cr_tmp = {
#                 'date_time': check_time,
#                 'date_time_last': date_time_last,
#                 'opening_price': price,
#                 'high_price': price,
#                 'low_price': price,
#                 'trade_price': price,
#                 'candle_acc_trade_price': 0,
#                 'candle_acc_trade_volume': 0,
#             }
#         cr_list.append(cr_tmp)
#         check_time = datetime_convert(check_time, sec_delta=60*min_)
#     if reverse_:
#         cr_list.reverse()  # gcm과 순서가 동일하게 변경
#     return cr_list
# # gcm = get_candles_minutes('KRW-XRP', time_to_='2021-09-30T15:39:00', count_=200, sleep_=False)
# # cr = candles_raw(gcm)
# # pprint(cr[-2:])


def get_candles_api(market_, time_to_=False, unit_=1, count_=200, sleep_=0.1, reverse_=True):
    if unit_ not in [1, 3, 5, 10, 15, 30, 60, 240, 'days', 'weeks', 'months']:
        print('incorrect unit')
        return False
    if type(unit_) == int:
        url = "https://api.upbit.com/v1/candles/minutes/" + str(unit_)
    else:
        url = "https://api.upbit.com/v1/candles/" + unit_ + "/"

    to = datetime_convert(time_to_, to_str=False, to_utc=True) if time_to_ else ""
    querystring = {"market": market_, "to": to, "count": str(count_)}
    headers = {"Accept": "application/json"}
    if sleep_:
        sleep(sleep_)
    response = requests.request("GET", url, headers=headers, params=querystring).json()

    cr_list = []
    from_time = response[-1]['candle_date_time_kst']
    to_time = response[0]['candle_date_time_kst'] if not time_to_ else datetime_convert(time_to_, sec_delta=-60)
    check_time = from_time  # 먼 시점부터 현재 시점으로 진행: 입력시간이 -1번 인덱스에 저장(response와 순서가 반대)
    candle_dict = {candle['candle_date_time_kst']: candle for candle in response}
    remain_key_list = ['opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_price', 'candle_acc_trade_volume']

    min_delta = 60*24 if unit_ == 'days' else 60*24*7 if unit_ == 'weeks' else 0 if unit_ == 'months' else unit_
    month_delta = 1 if unit_ == 'months' else 0
    while check_time <= to_time:
        cr_tmp = {}
        if check_time in candle_dict:
            cr_tmp['date_time'] = check_time
            date_time_last = datetime_convert(candle_dict[check_time]['timestamp'])
            cr_tmp['date_time_last'] = date_time_last
            for rk in remain_key_list:
                cr_tmp[rk] = candle_dict[check_time][rk]
            price = cr_tmp['trade_price']
        else:  # 누락 시간 생성
            cr_tmp = {
                'date_time': check_time,
                'date_time_last': date_time_last,
                'opening_price': price,
                'high_price': price,
                'low_price': price,
                'trade_price': price,
                'candle_acc_trade_price': 0,
                'candle_acc_trade_volume': 0,
            }
        cr_list.append(cr_tmp)
        check_time = datetime_convert(check_time, sec_delta=60*min_delta, month_delta=month_delta)

    if reverse_:
        cr_list.reverse()  # gcm과 순서가 동일하게 변경

    return cr_list
# gca = get_candles_api('KRW-XRP', time_to_='2021-09-30T15:39:00', unit_='months', count_=200, sleep_=False)
# gca = get_candles_api('KRW-XRP', time_to_='2021-09-30T15:39:00', count_=200, sleep_=False)


