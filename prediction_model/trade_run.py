from prediction_model.ML_models.tapering_hell.preprocessing import *
from coinanser.upbit_api.post_order import *
from prediction_model.insert_db import *

gca = get_candles_api('KRW-ADA', time_to_='2021-01-03T21:54:00')
cr = candles_refine(gca)
check_stats(cr)
check_model(cr)

gca = get_candles_api('KRW-XRP')
cr = candles_refine(gca)
check_stats(cr)
check_model(cr)


def predict_market(market_, model_='prediction_model/ML_models/tapering_hell/cuda_test_0.2.pt'):
    start_date_time = datetime_convert(datetime.now())
    gca = get_candles_api(market_)
    if datetime_convert(gca[0]['date_time'], sec_delta=60) < start_date_time:
        return False, gca
    try:
        cr = candles_refine(gca)
    except ZeroDivisionError:
        return False, gca
    # if not check_stats(cr):
    #     return False
    if check_stats(cr):
        print(gca[0]['date_time'], check_stats(cr), market_)
    return check_model(cr, model_), gca


# trade_id, start_date_time, predict_model, model_version, market, bid_goal, ask_goal
def run_model_trade(market_, model_='prediction_model/ML_models/tapering_hell/cuda_test_0.2.pt'):
    start_date_time = datetime_convert(datetime.now())
    pm, gca = predict_market(market_, model_)
    if not pm:
        return False
    if pm < 0.005:
        return False

    date_id = re.sub('[:-]', '', start_date_time)
    trade_id = (market_ + '_' + date_id)
    predict_model, model_version = file_version_parser(model_)
    mean_price = gca[0]['candle_acc_trade_price'] / gca[0]['candle_acc_trade_volume']
    bid_goal = ceil_unit(mean_price * 0.999)
    ask_goal = ceil_unit(bid_goal * 1.005)
    result = {
        'trade_id': trade_id,
        'start_date_time': start_date_time,
        'predict_model': predict_model,
        'model_version': model_version,
        'market': market_,
        'bid_goal': bid_goal,
        'ask_goal': ask_goal,
        'run_status': 'wait',
        'bid_id': None,
        'ask_id': None,
    }
    return result


market_status = {}
bid_funds = 10000
market_all = get_market_all()
while True:
    for market in market_all:

        if market not in market_status:  # 예측 시작
            rmt = run_model_trade(market)
            if not rmt:
                continue
            market_status[market] = rmt
            bid_price = market_status[market]['bid_goal']
            bid_volume = round(bid_funds / bid_price, 8)
            bid_id = bid_order(market, price_=bid_price, volume_=bid_volume)  # 매수 시작
            print(datetime_convert(datetime.now()), 'bid_start:', market, bid_price)
            market_status[market]['run_state'] = 'run_bid'
            market_status[market]['bid_id'] = bid_id

        if market in market_status and market_status[market]['run_state'] == 'run_bid':
            market_status[market]['bid_view'] = view_order(market_status[market]['bid_id'])
            if market_status[market]['bid_view']['state'] != 'done':
                pm = predict_market(market)[0]
                if pm and pm < 0:  # 매수 취소
                    view_order(market_status[market]['bid_id'], delete=True)
                    print(datetime_convert(datetime.now()), 'bid_cancel:', market)
                    del market_status[market]
                continue

            bid_view_tmp = market_status[market]['bid_view']
            print(bid_view_tmp['trades'][-1]['created_at'].split('+')[0], 'bid_done:', market,
                  sum([float(t['funds']) for t in bid_view_tmp['trades']]) /
                  sum([float(t['volume']) for t in bid_view_tmp['trades']]))

            ask_price = market_status[market]['ask_goal']
            ask_volume = sum([float(k['volume']) for k in market_status[market]['bid_view']['trades']])
            ask_id = ask_order(market, price_=ask_price, volume_=ask_volume)  # 매도 시작
            print(datetime_convert(datetime.now()), 'ask_start:', market, ask_price)
            market_status[market]['run_state'] = 'run_ask'
            market_status[market]['ask_id'] = ask_id

        if market in market_status and market_status[market]['run_state'] == 'run_ask':
            market_status[market]['ask_view'] = view_order(market_status[market]['ask_id'])
            if market_status[market]['ask_view']['state'] != 'done':
                pm = predict_market(market)[0]
                if pm and pm < 0:  # 주문 취소
                    view_order(market_status[market]['ask_id'], delete=True)
                    print(datetime_convert(datetime.now()), 'ask_cancel:', market)
                    ask_volume = sum([float(k['volume']) for k in market_status[market]['bid_view']['trades']])
                    ask_id = ask_order(market, volume_=ask_volume)  # 시장가 매도
                    market_status[market]['ask_id'] = ask_id
                continue

            ask_view_tmp = market_status[market]['ask_view']
            print(ask_view_tmp['trades'][-1]['created_at'].split('+')[0], 'ask_done:', market,
                  sum([float(t['funds']) for t in ask_view_tmp['trades']]) /
                  sum([float(t['volume']) for t in ask_view_tmp['trades']]))

            bid_info = market_status[market]['bid_view']
            ask_info = market_status[market]['ask_view']
            converted_value = convert_result(market_status[market], bid_info=bid_info, ask_info=ask_info)
            insert_trade_result(converted_value)
            print(market, 'done!\n',
                  'bid:', sum([float(t['funds']) for t in bid_info['trades']]) / sum([float(t['volume']) for t in bid_info['trades']]),
                  'ask:', sum([float(t['funds']) for t in ask_info['trades']]) / sum([float(t['volume']) for t in ask_info['trades']]))
            del market_status[market]

