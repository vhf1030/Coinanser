from coinanser.data_handling.prediction_model.ML_models.tapering_hell.preprocessing import *
from coinanser.data_handling.prediction_model.insert_db import *
from coinanser.upbit_api.post_order import *
from coinanser.upbit_api.get_quotation import *


# gca = get_candles_api('KRW-ADA', time_to_='2021-01-03T21:54:00')
# cr = candles_refine(gca)
# check_stats(cr)
# check_model(cr)
#
# gca = get_candles_api('KRW-XRP')
# cr = candles_refine(gca)
# check_stats(cr)
# check_model(cr)


def predict_market(market_, model_path_):
    start_date_time = datetime_convert(datetime.now())
    gca = get_candles_api(market_)[1:]  # 현재 데이터 사용하지 않음!
    if datetime_convert(gca[0]['date_time'], sec_delta=120) < start_date_time:
        # print('datetime error:', start_date_time, gca[0]['date_time'])
        return False, gca
    try:
        cr = candles_refine(gca)
    except ZeroDivisionError:
        return False, gca
    if not check_stats(cr):  # 기준 조정 필요
        return False, gca
    cm = check_model(cr, model_path_)
    print(gca[0]['date_time'], gca[0]['date_time_last'], market_, cm)
    return cm, gca[0]


# trade_id, start_date_time, predict_model, model_version, market, bid_goal, ask_goal
def run_model_trade(market_, gca0_, model_path_):
    start_date_time = datetime_convert(datetime.now())
    date_id = re.sub('[:-]', '', start_date_time)
    trade_id = (market_ + '_' + date_id)
    predict_model, model_version = file_version_parser(model_path_)
    mean_price = gca0_['candle_acc_trade_price'] / gca0_['candle_acc_trade_volume']
    bid_goal = ceil_unit(mean_price * 0.997)
    ask_goal = ceil_unit(bid_goal * 1.005)
    result = {
        'trade_id': trade_id,
        'start_date_time': start_date_time,
        'predict_model': predict_model,
        'model_version': model_version,
        'market': market_,
        'bid_goal': bid_goal,
        'ask_goal': ask_goal,
        'run_state': 'wait',
        'bid_id': None,
        'ask_id': None,
    }
    return result


model_path = 'coinanser/data_handling/prediction_model/ML_models/tapering_hell/cuda_test_0.2.pt'
# market_status = {}  # DB에서 가져오는 방법 구현 필요!
market_status = {'KRW-GAS': {'trade_id': 'KRW-GAS_20220205T102214', 'start_date_time': '2022-02-05T10:22:14', 'predict_model': 'cuda_test', 'model_version': 0.2, 'market': 'KRW-GAS', 'bid_goal': 7365.0, 'ask_goal': 7405.0, 'run_state': 'run_ask', 'bid_id': 'KRW-GAS_bid_20220205T102214', 'ask_id': 'KRW-GAS_ask_20220205T102252', 'bid_view': {'uuid': 'dcee124d-be22-410e-8d4a-2480cb466c7a', 'side': 'bid', 'ord_type': 'limit', 'price': '7365.0', 'state': 'done', 'market': 'KRW-GAS', 'created_at': '2022-02-05T10:22:14+09:00', 'volume': '6.78886626', 'remaining_volume': '0.0', 'reserved_fee': '25.00000000245', 'remaining_fee': '0.05091649695', 'paid_fee': '24.9490835055', 'locked': '101.88391039695', 'executed_volume': '6.78886626', 'trades_count': 1, 'trades': [{'market': 'KRW-GAS', 'uuid': 'db701b03-bc9d-4e19-a0b8-e1483767a8a0', 'price': '7350.0', 'volume': '6.78886626', 'funds': '49898.167011', 'created_at': '2022-02-05T10:22:14+09:00', 'side': 'bid'}]}, 'bid_parsed': {'fund_sum': 49898.167011, 'volume_sum': 6.78886626, 'price_mean': 7350.0, 'fund_cons_fee': 49923.116094505494, 'last_time': '2022-02-05T10:22:14'}, 'ask_view': {'uuid': '41a54cff-1b0c-4fe4-bcc0-c8e721fd78c2', 'side': 'ask', 'ord_type': 'limit', 'price': '7390.0', 'state': 'wait', 'market': 'KRW-GAS', 'created_at': '2022-02-05T10:22:52+09:00', 'volume': '6.78886626', 'remaining_volume': '6.78886626', 'reserved_fee': '0.0', 'remaining_fee': '0.0', 'paid_fee': '0.0', 'locked': '6.78886626', 'executed_volume': '0.0', 'trades_count': 0, 'trades': []}}}
bid_funds = 50000
# market_all = get_market_all()
while True:
    print('진행중:', ', '.join([k for k in market_status]))
    # for market in market_status:
    #     print(market, market_status[market]['run_state'], '\n',
    #           '목표매수가:', market_status[market]['bid_goal'],
    #           '목표매도가:', market_status[market]['ask_goal'])
    for market in MARKET_ALL:
        if market not in market_status:  # 예측 시작
            pm, gca0 = predict_market(market, model_path)
            if not pm or pm < 0.005:
                continue
            rmt = run_model_trade(market, gca0, model_path)
            if rmt['ask_goal']/rmt['bid_goal'] > 1 + pm:
                continue
            market_status[market] = rmt
            bid_price = market_status[market]['bid_goal']
            bid_volume = round(bid_funds / bid_price, 8)
            bid_id = bid_order(market, price_=bid_price, volume_=bid_volume)  # 매수 시작
            print(datetime_convert(datetime.now()), 'bid_start:', market, bid_price, bid_id, '( predict:', pm, ')')
            market_status[market]['run_state'] = 'run_bid'
            market_status[market]['bid_id'] = bid_id
            upsert_trade_result(market_status[market])  # DB insert

        if market in market_status and market_status[market]['run_state'] == 'run_bid':
            market_status[market]['bid_view'] = view_order(market_status[market]['bid_id'])
            if market_status[market]['bid_view']['state'] != 'done':
                pm = predict_market(market, model_path)[0]
                if pm and pm < -0.01:  # 매수 취소
                    delete_view = view_order(market_status[market]['bid_id'], delete=True)
                    if 'error' not in delete_view:
                        print(datetime_convert(datetime.now()), 'bid_cancel:', market, '( predict:', pm, ')')
                        delete_trade_result(market_status[market]['trade_id'])  # DB delete
                        del market_status[market]
                continue
            market_status[market]['bid_parsed'] = order_parser(market_status[market]['bid_view'])
            upsert_trade_result(market_status[market])  # DB update
            print(market_status[market]['bid_parsed']['last_time'], 'bid_done:', market, market_status[market]['bid_parsed']['price_mean'])

            # ask_price = market_status[market]['ask_goal']
            ask_price = ceil_unit(market_status[market]['bid_parsed']['price_mean'] * 1.005)
            ask_volume = market_status[market]['bid_parsed']['volume_sum']
            ask_id = ask_order(market, price_=ask_price, volume_=ask_volume)  # 매도 시작
            print(datetime_convert(datetime.now()), 'ask_start:', market, ask_price, ask_id)
            market_status[market]['run_state'] = 'run_ask'
            market_status[market]['ask_id'] = ask_id

        if market in market_status and market_status[market]['run_state'] == 'run_ask':
            market_status[market]['ask_view'] = view_order(market_status[market]['ask_id'])
            if market_status[market]['ask_view']['state'] != 'done':
                pm = predict_market(market, model_path)[0]
                if pm and pm < -0.015:  # 주문 취소 후 시장가 매도
                # if (pm and pm < -0.01) or market == 'KRW-BTT':  # 강제 주문 취소 후 시장가 매도
                    delete_view = view_order(market_status[market]['ask_id'], delete=True)
                    if 'error' not in delete_view:
                        ask_volume = order_parser(market_status[market]['bid_view'])['volume_sum']
                        ask_id = ask_order(market, volume_=ask_volume)  # 시장가 매도
                        print(datetime_convert(datetime.now()), 'ask_cancel:', market, ask_id, '( predict:', pm, ')')
                        market_status[market]['ask_id'] = ask_id
                continue
            market_status[market]['ask_parsed'] = order_parser(market_status[market]['ask_view'])
            upsert_trade_result(market_status[market])  # DB update
            print(market_status[market]['ask_parsed']['last_time'], 'ask_done:', market, market_status[market]['ask_parsed']['price_mean'])
            print(market, 'done!\n',
                  'bid:', market_status[market]['bid_parsed']['price_mean'],
                  'ask:', market_status[market]['ask_parsed']['price_mean'])
            del market_status[market]

