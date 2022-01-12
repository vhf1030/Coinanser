from my_setting.config import PYMYSQL_CONNECT
from coinanser.upbit_api.post_order import *
import pymysql


conn = pymysql.connect(
    user=PYMYSQL_CONNECT['user'],
    passwd=PYMYSQL_CONNECT['passwd'],
    host=PYMYSQL_CONNECT['host'],
    db=PYMYSQL_CONNECT['db'],
    charset=PYMYSQL_CONNECT['charset'],
)
cursor = conn.cursor(pymysql.cursors.DictCursor)


def upsert_trade_result(trade_info):
    trade_column = ['trade_id', 'start_date_time', 'predict_model', 'model_version', 'market', 'bid_goal', 'ask_goal']
    result = [trade_info[c] for c in trade_column]
    if 'bid_parsed' in trade_info:
        bid_date_time = trade_info['bid_parsed']['last_time']
        bid_price = trade_info['bid_parsed']['price_mean']
        bid_volume = trade_info['bid_parsed']['volume_sum']
        bid_funds = trade_info['bid_parsed']['fund_cons_fee']
        result.extend([bid_date_time, bid_price, bid_volume, bid_funds])
    else:
        result.extend([None, None, None, None])
    if 'ask_parsed' in trade_info:
        ask_date_time = trade_info['ask_parsed']['last_time']
        ask_price = trade_info['ask_parsed']['price_mean']
        ask_volume = trade_info['ask_parsed']['volume_sum']
        ask_funds = trade_info['ask_parsed']['fund_cons_fee']
        result.extend([ask_date_time, ask_price, ask_volume, ask_funds])
    else:
        result.extend([None, None, None, None])

    values = tuple([str(r) if r else r for r in result + result[-8:]])
    # command = 'INSERT INTO ' if not update else 'UPDATE '
    # sql = command + """
    sql = """
    INSERT INTO `coinanser_traderesults` (
        trade_id, start_date_time, predict_model, model_version, market, bid_goal, ask_goal,
        bid_date_time, bid_price, bid_volume, bid_funds,
        ask_date_time, ask_price, ask_volume, ask_funds
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        bid_date_time=%s, bid_price=%s, bid_volume=%s, bid_funds=%s,
        ask_date_time=%s, ask_price=%s, ask_volume=%s, ask_funds=%s
    """
    cursor.execute(sql, values)
    conn.commit()
    return
    # """ % ("'" + "', '".join(values) + "'")


def delete_trade_result(trade_id):
    sql = """
    DELETE FROM `coinanser_traderesults`
    WHERE trade_id = '%s'
    """ % trade_id
    cursor.execute(sql)
    conn.commit()
    return

