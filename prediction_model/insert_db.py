from my_setting.config import PYMYSQL_CONNECT
import pymysql


conn = pymysql.connect(
    user=PYMYSQL_CONNECT['user'],
    passwd=PYMYSQL_CONNECT['passwd'],
    host=PYMYSQL_CONNECT['host'],
    db=PYMYSQL_CONNECT['db'],
    charset=PYMYSQL_CONNECT['charset'],
)
cursor = conn.cursor(pymysql.cursors.DictCursor)


def convert_result(trade_info, bid_info=False, ask_info=False):
    trade_column = ['trade_id', 'start_date_time', 'predict_model', 'model_version', 'market', 'bid_goal', 'ask_goal']
    result = [trade_info[c] for c in trade_column]

    if bid_info:
        bid_date_time = bid_info['trades'][-1]['created_at'].split('+')[0]
        bid_funds = sum([float(t['funds']) for t in bid_info['trades']])
        bid_volume = sum([float(t['volume']) for t in bid_info['trades']])
        bid_price = bid_funds / bid_volume
        result.extend([bid_date_time, bid_price, bid_volume, bid_funds])
    else:
        result.extend([None, None, None, None])
    if ask_info:
        ask_date_time = ask_info['trades'][-1]['created_at'].split('+')[0]
        ask_funds = sum([float(t['funds']) for t in ask_info['trades']])
        ask_volume = sum([float(t['volume']) for t in ask_info['trades']])
        ask_price = ask_funds / ask_volume
        result.extend([ask_date_time, ask_price, ask_volume, ask_funds])
    else:
        result.extend([None, None, None, None])
    return tuple([str(r) for r in result])


def insert_trade_result(values):
    sql = """
    INSERT INTO `coinanser_traderesults` (
        trade_id, start_date_time, predict_model, model_version, market, bid_goal, ask_goal,
        bid_date_time, bid_price, bid_volume, bid_funds,
        ask_date_time, ask_price, ask_volume, ask_funds
    ) VALUES (%s)
    """ % ("'" + "', '".join(values) + "'")
    cursor.execute(sql)
    conn.commit()
    return




