import requests
import math
from time import sleep
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint
from common.utils import datetime_convert
from coinanser.views.db_handler import create_rawdata_table, upsert_rawdata_table
# create_rawdata_table('test123')


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
        if market_dict[md]['market_warning'] != 'NONE':
            print(md, '- market warning:', market_dict[md]['market_warning'])
    if print_:
        print('market 수:', len(market_dict))
        print('markets:', ', '.join([market_dict[market]['korean_name'] for market in market_dict]))
    return market_dict
MARKET_ALL = get_market_all()


def get_upbit_quotation(market_, time_to_=False, unit_=1, count_=200, sleep_=0.1):
    if unit_ not in [1, 3, 5, 10, 15, 30, 60, 240, 'days', 'weeks', 'months']:
        print('incorrect unit')
        return False
    if type(unit_) == int:
        url = "https://api.upbit.com/v1/candles/minutes/" + str(unit_)
    if type(unit_) == str:
        url = "https://api.upbit.com/v1/candles/" + unit_ + "/"
    to = datetime_convert(time_to_, to_str=False, to_utc=True) if time_to_ else ""
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


def refine_rawdata(rawdata):
    # 누락된 시간의 데이터 삽입 및 평균 계산
    # market view 에 사용(API/DB -> view) / training handler 에서는 사용하지 않음
    date_time = rawdata[-1]['candle_date_time_kst']  # 먼 시점부터 현재 시점으로 진행
    unit = rawdata[0]['unit']
    min_delta = (
        0 if unit == 'months' else
        60 * 24 * 7 if unit == 'weeks' else
        60 * 24 if unit == 'days' else
        unit
    )
    month_delta = 1 if unit == 'months' else 0
    refdata_list = []
    while rawdata:
        if date_time == rawdata[-1]['candle_date_time_kst']:  # 데이터가 존재할 때
            tmp = rawdata.pop()
            date_time_last = datetime_convert(tmp['timestamp'])
            opening_price = tmp['opening_price']
            high_price = tmp['high_price']
            low_price = tmp['low_price']
            trade_price = tmp['trade_price']
            mean_price = tmp['candle_acc_trade_price'] / tmp['candle_acc_trade_volume']
            candle_acc_trade_price = tmp['candle_acc_trade_price']
            candle_acc_trade_volume = tmp['candle_acc_trade_volume']
        else:
            opening_price, high_price, low_price, mean_price = trade_price, trade_price, trade_price, trade_price
            candle_acc_trade_price, candle_acc_trade_volume = 0, 0
        ref_tmp = {
            'date_time': date_time,
            'date_time_last': date_time_last,                    # 데이터가 없는 경우 직전의 마지막 거래시간을 반영
            'opening_price': opening_price,                      # 데이터가 없는 경우 직전의 종가를 반영
            'high_price': high_price,                            # 데이터가 없는 경우 직전의 종가를 반영
            'low_price': low_price,                              # 데이터가 없는 경우 직전의 종가를 반영
            'trade_price': trade_price,                          # 데이터가 없는 경우 직전의 종가를 반영
            'mean_price': mean_price,                            # 데이터가 없는 경우 직전의 종가를 반영
            'candle_acc_trade_price': candle_acc_trade_price,    # 데이터가 없는 경우 0
            'candle_acc_trade_volume': candle_acc_trade_volume,  # 데이터가 없는 경우 0
        }
        refdata_list.append(ref_tmp)
        date_time = datetime_convert(date_time, sec_delta=60 * min_delta, month_delta=month_delta)
    refdata_list.reverse()  # 최근 시간부터 출력
    return refdata_list
# uq = get_upbit_quotation('KRW-JST', time_to_='2022-01-25T17:42:00', unit_=1, count_=200, sleep_=False)
# sr = select_rawdata('rawdata_2201', 'KRW-JST', time_to_='2022-01-25T17:42:00')
# uq[0] == sr[0]
# pprint(sr[0])
# # {'candle_acc_trade_price': 3779962.18328235,
# #  'candle_acc_trade_volume': 81390.27103833,
# #  'candle_date_time_kst': '2022-01-25T17:41:00',
# #  'candle_date_time_utc': '2022-01-25T08:41:00',
# #  'high_price': 46.6,
# #  'low_price': 46.4,
# #  'market': 'KRW-JST',
# #  'opening_price': 46.4,
# #  'timestamp': 1643100119633,
# #  'trade_price': 46.5,
# #  'unit': 1}
# for r in refine_rawdata(uq):
#      print(r['date_time'], r['date_time_last'], r['candle_acc_trade_price'], r['mean_price'], r['trade_price'])


# TODO: rawdata DB insert 작업 자동화
def run_rawdata_insert(market_list, s_time, e_time):
    for market in market_list:
        time_to = e_time
        # table_name = 'rawdata_' + datetime_convert(time_to, to_str=False, sec_delta=-1).strftime("%y%m")
        table_suf = datetime_convert(time_to, to_str=False, sec_delta=-1).strftime("%y%m")
        while s_time < time_to:
            print(market, time_to)
            uq = get_upbit_quotation(market, time_to_=time_to)
            if not uq:  # data 없는 경우 중단
                break
            while table_suf != datetime_convert(uq[-1]['candle_date_time_kst'], to_str=False).strftime("%y%m"):
                uq.pop()  # 이전 데이터는 insert 하지 않음
            upsert_rawdata_table('rawdata_' + table_suf, uq)
            time_to = uq[-1]['candle_date_time_kst']
            # table_suf 변경 작업 필요


# run_rawdata_insert(MARKET_ALL, '2022-01-01T00:00:00', '2022-02-01T00:00:00')

# get_upbit_quotation('KRW-JST', time_to_='2022-01-25T17:42:00')[-1]

market, s_time, e_time = 'KRW-WEMIX', '2022-01-01T00:00:00', '2022-02-01T00:00:00'
