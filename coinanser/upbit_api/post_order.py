import re
import time
from coinanser.upbit_api.get_account import *
from coinanser.upbit_api.utils import *
# # 소스코드 실행시
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()


# 매수주문
def bid_order(market_, price_, volume_=0):
    date_id = re.sub('[:-]', '', datetime_convert(datetime.now()))
    identifier = (market_ + '_bid_' + date_id)
    query = {
        'market': market_,
        'side': 'bid',
        'ord_type': 'price',  # 시장가 매수
        'identifier': identifier,
        'price': str(price_)
    }
    if volume_:  # 지정가 매수
        query['volume'] = str(volume_)
        query['ord_type'] = 'limit'

    payload = get_query_payload(query)
    headers = {"Authorization": get_authorize_token(payload)}
    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    if res.status_code != 201:
        print(res.json()['error']['message'])
    time.sleep(0.125)
    return identifier
# bid_order('KRW-BTC', 10000, volume_=0)  # 시장가 매수
# bid_order('KRW-FLOW', 10000, volume_=1)  # 지정가 매수


# 매도주문
def ask_order(market_, volume_, price_=0):
    date_id = re.sub('[:-]', '', datetime_convert(datetime.now()))
    identifier = (market_ + '_ask_' + date_id)
    query = {
        'market': market_,
        'side': 'ask',
        'ord_type': 'market',  # 시장가 매도
        'identifier': identifier,
        'volume': str(volume_)
    }
    if price_:  # 지정가 매도
        query['price'] = str(price_)
        query['ord_type'] = 'limit'

    payload = get_query_payload(query)
    headers = {"Authorization": get_authorize_token(payload)}
    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    if res.status_code != 201:
        print(res.json()['error']['message'])
    time.sleep(0.125)
    return identifier
# conc_volume = sum([float(k['volume']) for k in view_order('KRW-BTC_bid_20220106T124542')['trades']])
# ask_order('KRW-BTC', conc_volume, price_=0)  # 시장가 매도
# ask_order('KRW-FLOW', 1, price_=10000)  # 지정가 매도


def view_order(identifier_, delete=False):
    query = {'identifier': identifier_}
    payload = get_query_payload(query)
    headers = {"Authorization": get_authorize_token(payload)}
    if delete:
        res = requests.delete(server_url + "/v1/order", params=query, headers=headers)
    else:
        res = requests.get(server_url + "/v1/order", params=query, headers=headers)
    if res.status_code != 200:
        print(res.json()['error']['message'])
    time.sleep(0.125)
    return res.json()
# view_order('KRW-FLOW_bid_20220106T124706')  # 주문조회
# view_order('KRW-FLOW_bid_20220106T124706', delete=True)  # 주문취소

# bid_order('KRW-BTC', 10000, volume_=0)  # 시장가 매수
# # 'KRW-BTC_bid_20220106T132228'
# pprint(view_order('KRW-BTC_bid_20220106T132228'))
# # {'created_at': '2022-01-06T13:22:28+09:00',
# #  'executed_volume': '0.00018964',
# #  'locked': '0.2829414',
# #  'market': 'KRW-BTC',
# #  'ord_type': 'price',
# #  'paid_fee': '4.9998586',
# #  'price': '10000.0',
# #  'remaining_fee': '0.0001414',
# #  'remaining_volume': None,
# #  'reserved_fee': '5.0',
# #  'side': 'bid',
# #  'state': 'cancel',
# #  'trades': [{'created_at': '2022-01-06T13:22:28+09:00',
# #              'funds': '9999.7172',
# #              'market': 'KRW-BTC',
# #              'price': '52730000.0',
# #              'side': 'bid',
# #              'uuid': '200a3ec1-757d-4a17-bc72-f4f9031fdb2d',
# #              'volume': '0.00018964'}],
# #  'trades_count': 1,
# #  'uuid': '08d005c5-1a2f-40b7-a2a3-13115c4c4964',
# #  'volume': None}

# conc_volume = sum([float(k['volume']) for k in view_order('KRW-BTC_bid_20220106T132228')['trades']])
# # 0.00018964
# ask_order('KRW-BTC', conc_volume, price_=0)  # 시장가 매도
# # 'KRW-BTC_ask_20220106T133347'
# pprint(view_order('KRW-BTC_ask_20220106T133347'))
# # {'created_at': '2022-01-06T13:33:47+09:00',
# #  'executed_volume': '0.00018964',
# #  'locked': '0.0',
# #  'market': 'KRW-BTC',
# #  'ord_type': 'market',
# #  'paid_fee': '4.99587616',
# #  'price': None,
# #  'remaining_fee': '0.0',
# #  'remaining_volume': '0.0',
# #  'reserved_fee': '0.0',
# #  'side': 'ask',
# #  'state': 'done',
# #  'trades': [{'created_at': '2022-01-06T13:33:47+09:00',
# #              'funds': '9991.75232',
# #              'market': 'KRW-BTC',
# #              'price': '52688000.0',
# #              'side': 'ask',
# #              'uuid': '68c85796-8a21-413f-a485-304a0a57c6a5',
# #              'volume': '0.00018964'}],
# #  'trades_count': 1,
# #  'uuid': '68b0fdc6-df39-4cd1-ac53-b4485ffd3091',
# #  'volume': '0.00018964'}



