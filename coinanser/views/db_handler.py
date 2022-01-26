from my_setting.config import PYMYSQL_CONNECT
from datetime import datetime, timedelta
from common.utils import datetime_convert
import pymysql


conn = pymysql.connect(
    user=PYMYSQL_CONNECT['user'],
    passwd=PYMYSQL_CONNECT['passwd'],
    host=PYMYSQL_CONNECT['host'],
    db=PYMYSQL_CONNECT['db'],
    charset=PYMYSQL_CONNECT['charset'],
)
cursor = conn.cursor(pymysql.cursors.DictCursor)

RAWDATA_COLUMNS = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
                   'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume']


def create_rawdata_table(table_name):
    sql = '''
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'test'
        AND table_name = '%s'
        ''' % table_name
    if cursor.execute(sql):
        print("table('" + table_name + "') already exists")
        return
    else:
        sql = '''CREATE TABLE `test`.`%s` (
            `market` VARCHAR(15) NOT NULL,
            `candle_date_time_kst` DATETIME NOT NULL,
            `opening_price` FLOAT NOT NULL,
            `high_price` FLOAT NOT NULL,
            `low_price` FLOAT NOT NULL,
            `trade_price` FLOAT NOT NULL,
            `timestamp` BIGINT NOT NULL,
            `candle_acc_trade_price` DOUBLE NOT NULL,
            `candle_acc_trade_volume` DOUBLE NOT NULL,
            `candle_date_time_utc` DATETIME NOT NULL,
            `check_date_time` TIMESTAMP DEFAULT NOW(),
            UNIQUE INDEX `market_date_time_UNIQUE` (`candle_date_time_kst`, `market`),
            INDEX (`market`)
            )ENGINE = MyISAM;
            ''' % table_name
        cursor.execute(sql)
        conn.commit()
        print(sql)
        return
# table_name = 'rawdata_' + datetime_convert('2022-01-25T09:14:00', to_str=False).strftime("%y%m")
# create_rawdata_table(table_name)


def upsert_rawdata_table(table_name, uq_):
    columns = RAWDATA_COLUMNS
    val = [tuple(u[c] for c in columns) for u in uq_]
    sql = ("INSERT INTO `test`.`" + table_name + "` (" + ', '.join(columns) +
           ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" +
           " ON DUPLICATE KEY UPDATE " +
           ', '.join([c + ' = VALUES(' + c + ')' for c in columns]) +
           ", check_date_time = default;")  # data 시간을 확인시간과 비교하여 데이터가 완전히 수집되었는지 확인 가능
    cursor.executemany(sql, val)
    conn.commit()

# uq = get_upbit_quotation('KRW-JST', unit_=1, count_=10, sleep_=False)
# insert_rawdata_table(table_name, uq)


def select_rawdata(table_name, market, time_to_=False, count_=200):
    time_to = datetime.now() if not time_to_ else time_to_
    columns = RAWDATA_COLUMNS  # get_upbit_quotation 과 형식을 맞추기 위해 check_date_time 은 받아오지 않음
    sql = ("SELECT %s " % ', '.join(columns) +
           "FROM `test`.`%s`" % table_name +
           "WHERE (candle_date_time_kst < '%s' AND market = '%s')" % (time_to, market) +
           "ORDER BY candle_date_time_kst ASC LIMIT %s;" % count_)
    cursor.execute(sql)
    selected = cursor.fetchall()
    result = []
    while selected:
        tmp = selected.pop()
        for k in ['candle_date_time_kst', 'candle_date_time_utc']:
            tmp[k] = datetime_convert(tmp[k])
        tmp['unit'] = 1

        result.append(tmp)
    return result
# sr = select_rawdata(table_name, 'KRW-JST')
# for s in sr:
#     print(s['candle_date_time_kst'])
# pq = prep_quotation(sr)

# sql = """
# INSERT INTO `rawdata_2201` (
#     market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price,
#     timestamp, candle_acc_trade_price, candle_acc_trade_volume
# ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# """
#
# cursor.execute(sql, ['KRW-JST', '2022-01-25T06:15:00', '2022-01-25T15:15:00', 46.8, 46.8, 46.8, 46.8, 1643092535553, 24165.85084898, 516.36433438])
# conn.commit()
#
# sql = """
# INSERT INTO `rawdata_2201`
# VALUES (
#     %(market)s,
#     %(candle_date_time_utc)s,
#     %(candle_date_time_kst)s,
#     %(opening_price)s,
#     %(high_price)s,
#     %(low_price)s,
#     %(trade_price)s,
#     %(timestamp)s,
#     %(candle_acc_trade_price)s,
#     %(candle_acc_trade_volume)s
#     )
# """



# Create rawdata table
# market_all = get_market_all()
# for market in market_all:
#     table_name = 'rawdata_' + market
#     sql = '''
#     SELECT 1 FROM information_schema.tables
#     WHERE table_schema = 'coinanser'
#     AND table_name = '%s'
#     ''' % table_name
#     if not cursor.execute(sql):
#         sql = '''CREATE TABLE `coinanser`.`%s` (
#             `date_time` DATETIME NOT NULL,
#             `date_time_last` DATETIME NULL,
#             `opening_price` DOUBLE NULL,
#             `high_price` DOUBLE NULL,
#             `low_price` DOUBLE NULL,
#             `trade_price` DOUBLE NULL,
#             `candle_acc_trade_price` DOUBLE NULL,
#             `candle_acc_trade_volume` DOUBLE NULL,
#             PRIMARY KEY (`date_time`)
#             )ENGINE = MyISAM;
#             ''' % table_name
#         cursor.execute(sql)
#         coinanser_conn.commit()

