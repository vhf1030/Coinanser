from common.utils import datetime_convert
# from coinanser.data_handling.db_handler import get_db_rawdata, upsert_atpu_table
# from coinanser.data_handling.rawdata_handler import MARKET_ALL


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
                'check_date_time': end['check_date_time']
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



