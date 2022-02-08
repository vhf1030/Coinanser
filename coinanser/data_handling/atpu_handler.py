from common.utils import datetime_convert
from coinanser.data_handling.db_handler import get_db_rawdata, upsert_atpu_table
from coinanser.data_handling.rawdata_handler import MARKET_ALL


def atpu_converter(rawdata):
    # 거래금액 100 억 단위 기준으로 data 변환
    result, stack = [], []
    atp_sum, atv_sum = 0, 0
    for r in rawdata:
        stack.append(r)
        atp_sum += r['candle_acc_trade_price']
        atv_sum += r['candle_acc_trade_volume']
        while atp_sum > 10000000000:
            high_price, low_price = max([s['high_price'] for s in stack]), min([s['low_price'] for s in stack])
            end = stack.pop(0)
            duration = datetime_convert(end['timestamp'], to_str=False) - datetime_convert(r['candle_date_time_kst'], to_str=False)
            res_tmp = {
                'market': r['market'],
                'e_date_time': end['candle_date_time_kst'],
                's_date_time': r['candle_date_time_kst'],
                'duration': duration.days * 24 * 60 * 60 + duration.seconds,
                'opening_price': r['opening_price'],
                'high_price': high_price,
                'low_price': low_price,
                'trade_price': end['trade_price'],
                'mean_price': atp_sum / atv_sum,
                'atp_sum': atp_sum,
            }
            atp_sum -= end['candle_acc_trade_price']
            atv_sum -= end['candle_acc_trade_volume']
            result.append(res_tmp)
    return result
# rawdata = get_db_rawdata('KRW-NEAR', '2022-02-01T01:01:00', 1000)
# rawdata[0]
# atpu = atpu_converter(rawdata)
# for a in atpu:
#     print(a['e_date_time'], a['duration'])
# sum([t['duration'] for t in test]) / len(test) / 60


def run_atpu_insert(market_list, s_time, e_time):
    for market in market_list:
        time_to = e_time
        count = 200
        # table_name = 'rawdata_' + datetime_convert(time_to, to_str=False, sec_delta=-1).strftime("%y%m")
        while s_time < time_to:
            print(market, time_to, count)
            rawdata = get_db_rawdata(market, time_to_=time_to, count_=count)
            if not rawdata:  # DB 내에 rawdata 없는 경우 중단
                break
            atpu = atpu_converter(rawdata)
            if not atpu:
                count *= 4
                continue
            if len(atpu) < 100:
                count *= 2
            first_time = atpu[0]['e_date_time']
            if first_time < s_time:  # 기준 시간보다 이전인 경우 중단
                break
            table_suf = datetime_convert(first_time, to_str=False).strftime("%y%m")  # router 부분
            while table_suf != datetime_convert(atpu[-1]['e_date_time'], to_str=False).strftime("%y%m"):
                atpu.pop()  # 이전 달의 데이터는 insert 하지 않음
            upsert_atpu_table('atpu_' + table_suf, atpu)
            time_to = atpu[-1]['e_date_time']
            if len(atpu) > 200:
                count //= 2
    return


# run_atpu_insert(MARKET_ALL, '2022-01-01T00:00:00', '2022-02-02T00:00:00')

# run_atpu_insert(['KRW-WEMIX'], '2022-01-01T00:00:00', '2022-02-02T00:00:00')

# # 월 초 시간이 출력되는 이유 - run function 상에서 table에 해당하지 않는 데이터를 제거함
# # KRW-ETH 2022-02-01T01:50:00 200
# # KRW-ETH 2022-02-01T00:00:00 200
# # KRW-MTL 2022-02-02T00:00:00 12800
# # KRW-MTL 2022-02-01T00:00:00 6400

# market, s_time, e_time = 'KRW-WEMIX', '2022-01-01T00:00:00', '2022-02-02T00:00:00'
# get_db_rawdata('KRW-QKC', '2022-02-01T00:01:00', 200)

# sum([r['candle_acc_trade_price'] for r in rawdata])
# test = get_db_rawdata('KRW-QKC', time_to_='2022-02-02T00:00:00', count_=3200)
# test[-1]
# len(test)
# for t in test:
#     print(t['candle_date_time_kst'])



