import requests
import math
from time import sleep
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint
from coinanser.upbit_api.utils import datetime_convert


# Get data api - https://docs.upbit.com/reference/
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
# MARKET_ALL = get_market_all()


def get_upbit_quotation(market_, time_to_=False, unit_=1, count_=200, sleep_=0.1):
    if unit_ not in [1, 3, 5, 10, 15, 30, 60, 240, 'days', 'weeks', 'months']:
        print('incorrect unit')
        return False
    if type(unit_) == int:
        url = "https://api.upbit.com/v1/candles/minutes/" + str(unit_)
    if type(unit_) == str:
        url = "https://api.upbit.com/v1/candles/" + unit_ + "/"
    to = datetime_convert(time_to_, to_str=False, to_utc=True, sec_delta=1) if time_to_ else ""
    querystring = {"market": market_, "to": to, "count": str(count_)}
    headers = {"Accept": "application/json"}
    if sleep_:
        sleep(sleep_)
    response = requests.request("GET", url, headers=headers, params=querystring).json()  # 최근 시간부터 출력
    if type(unit_) == str:
        for r in response:
            r['unit'] = unit_
    return response
# uq = get_upbit_quotation('KRW-XRP', unit_='months', count_=200, sleep_=False)
# uq = get_upbit_quotation('KRW-JST', unit_=1, count_=200, sleep_=False)


def prep_quotation(uq):
    # market view(임시), training handler 에서 사용
    check_time = uq[-1]['candle_date_time_kst']  # 먼 시점부터 현재 시점으로 진행
    unit = uq[0]['unit']
    min_delta = 60 * 24 if unit == 'days' else 60 * 24 * 7 if unit == 'weeks' else 0 if unit == 'months' else unit
    month_delta = 1 if unit == 'months' else 0
    cr_list = []
    while uq:
        if check_time == uq[-1]['candle_date_time_kst']:
            cr_tmp = uq.pop()
            cr_tmp['date_time'] = check_time
            cr_tmp['date_time_last'] = datetime_convert(cr_tmp['timestamp'])
            cr_tmp['mean_price'] = cr_tmp['candle_acc_trade_price'] / cr_tmp['candle_acc_trade_volume']
            cr_list.append(cr_tmp)
        else:  # 누락 시간 생성
            cr_tmp = {
                'date_time': check_time,
                'date_time_last': cr_list[-1]['date_time_last'],
                'opening_price': cr_list[-1]['trade_price'],
                'high_price': cr_list[-1]['trade_price'],
                'low_price': cr_list[-1]['trade_price'],
                'trade_price': cr_list[-1]['trade_price'],
                'mean_price': cr_list[-1]['trade_price'],
                'candle_acc_trade_price': 0,
                'candle_acc_trade_volume': 0,
            }
            cr_list.append(cr_tmp)
        check_time = datetime_convert(check_time, sec_delta=60 * min_delta, month_delta=month_delta)
    cr_list.reverse()  # 최근 시간부터 출력
    return cr_list
# uq = get_upbit_quotation('KRW-JST', time_to_='2022-01-25T17:42:01', unit_=1, count_=200, sleep_=False)
# sr = select_rawdata(table_name, 'KRW-JST', time_to_='2022-01-25T17:42:01')
# uq[0] == sr[0]
# pprint(sr[0])
# # {'candle_acc_trade_price': 248083.0499998,
# #  'candle_acc_trade_volume': 5312.27087794,
# #  'candle_date_time_kst': '2022-01-25T17:42:00',
# #  'candle_date_time_utc': '2022-01-25T08:42:00',
# #  'high_price': 46.7,
# #  'low_price': 46.7,
# #  'market': 'KRW-JST',
# #  'opening_price': 46.7,
# #  'timestamp': 1643100135822,
# #  'trade_price': 46.7,
# #  'unit': 1}
