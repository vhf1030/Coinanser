from my_setting.config import PYMYSQL_CONNECT
from datetime import datetime, timedelta
from common.utils import datetime_convert
import pymysql
from coinanser.data_handling.rawdata_handler import get_upbit_quotation
from coinanser.data_handling.atpu_handler import atpu_converter


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
ATPU_COLUMNS = ['market', 'e_date_time', 's_date_time', 'duration', 'opening_price',
                'high_price', 'low_price', 'trade_price', 'mean_price', 'atp_sum']


def check_table(table_name):
    sql = '''
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'test'
    AND table_name = '%s'
    ''' % table_name
    return cursor.execute(sql)
# check_table('rawdata_2301')


def create_rawdata_table(table_name):
    if check_table(table_name):
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
    try:
        cursor.executemany(sql, val)
    except pymysql.err.ProgrammingError:
        create_rawdata_table(table_name)  # table 없는 경우 생성
        cursor.executemany(sql, val)
    conn.commit()
# uq = get_upbit_quotation('KRW-JST', unit_=1, count_=10, sleep_=False)
# upsert_rawdata_table(table_name, uq)


def run_rawdata_insert(market_list, s_time, e_time):
    for market in market_list:
        time_to = e_time
        # table_name = 'rawdata_' + datetime_convert(time_to, to_str=False, sec_delta=-1).strftime("%y%m")
        while s_time < time_to:
            print(market, time_to)
            uq = get_upbit_quotation(market, time_to_=time_to)
            if not uq:  # upbit api data 없는 경우 중단
                break
            first_time = uq[0]['candle_date_time_kst']
            if first_time < s_time:  # 기준 시간보다 이전인 경우 중단
                break
            table_suf = datetime_convert(first_time, to_str=False).strftime("%y%m")  # router 부분
            while table_suf != datetime_convert(uq[-1]['candle_date_time_kst'], to_str=False).strftime("%y%m"):
                uq.pop()  # 이전 달의 데이터는 insert 하지 않음
            upsert_rawdata_table('rawdata_' + table_suf, uq)
            time_to = uq[-1]['candle_date_time_kst']
    return
# run_rawdata_insert(MARKET_ALL, '2022-02-01T00:00:00', '2022-02-11T14:00:00')
# run_rawdata_insert(['KRW-JST', 'KRW-WEMIX'], '2021-12-01T00:00:00', '2022-01-01T00:00:00')

# market_remain = ['KRW-WEMIX']
# run_rawdata_insert(market_remain, '2022-01-01T00:00:00', '2022-02-02T00:00:00')

# get_upbit_quotation('KRW-JST', time_to_='2022-01-25T17:42:00')[-1]
# market, s_time, e_time = 'KRW-WEMIX', '2022-01-01T00:00:00', '2022-02-02T00:00:00'


def select_rawdata(table_name, market, time_to, limit_=200):
    columns = RAWDATA_COLUMNS  # get_upbit_quotation 과 형식을 맞추기 위해 check_date_time 은 받아오지 않음
    results = []
    sql = ("SELECT %s " % ', '.join(columns) +
           "FROM `test`.`%s`" % table_name +
           "WHERE (candle_date_time_kst < '%s' AND market = '%s')" % (time_to, market) +
           "ORDER BY candle_date_time_kst DESC LIMIT %s;" % limit_)
    try:
        cursor.execute(sql)
    except pymysql.err.ProgrammingError as e:
        print('pymysql error:', e.args[1])
        return results
    selected = cursor.fetchall()
    for s in selected:
        for k in ['candle_date_time_kst', 'candle_date_time_utc']:
            s[k] = datetime_convert(s[k])
        s['unit'] = 1
        results.append(s)
    return results
# tr = tb_rawdata('rawdata_2201', 'KRW-JST', '2022-01-11T19:01:00')
# for t in tr:
#     print(t['candle_date_time_kst'])
# pq = prep_quotation(sr)


def get_db_rawdata(market, time_to_=False, count_=200):
    # DB select 시 table 접근 방법 설정 router 포함
    time_to = datetime.now() if not time_to_ else datetime_convert(time_to_, to_str=False)
    table_name = 'rawdata_' + time_to.strftime("%y%m")
    results = []
    while len(results) < count_:
        sr = select_rawdata(table_name, market, time_to, limit_=count_)
        if not sr:
            # router 부분
            time_to = (time_to - timedelta(seconds=1)).replace(hour=0, minute=0, second=0)
            table_name = 'rawdata_' + time_to.strftime("%y%m")
            if not check_table(table_name):
                return results
            continue
        results.extend(sr)
        time_to = datetime_convert(results[-1]['candle_date_time_kst'], to_str=False)
    return results[:count_]
# sr = get_db_rawdata('KRW-BTC', '2022-01-01T01:01:00', 300)
# sr = get_db_rawdata('KRW-BTC', '2021-12-01T01:01:00', 300)
# for i, s in enumerate(sr):
#     print(i, s['candle_date_time_kst'])
# len(sr)


def create_atpu_table(table_name):
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
            `e_date_time` DATETIME NOT NULL,
            `s_date_time` DATETIME NOT NULL,
            `duration` INT NOT NULL,
            `opening_price` FLOAT NOT NULL,
            `high_price` FLOAT NOT NULL,
            `low_price` FLOAT NOT NULL,
            `trade_price` FLOAT NOT NULL,
            `mean_price` FLOAT NOT NULL,
            `atp_sum` DOUBLE NOT NULL,
            `check_date_time` TIMESTAMP DEFAULT NOW(),
            UNIQUE INDEX `market_date_time_UNIQUE` (`e_date_time`, `market`),
            INDEX (`market`)
            )ENGINE = MyISAM;
            ''' % table_name
        cursor.execute(sql)
        conn.commit()
        print(sql)
        return


def upsert_atpu_table(table_name, atpu):
    columns = ATPU_COLUMNS
    val = [tuple(r[c] for c in columns) for r in atpu]
    sql = ("INSERT INTO `test`.`" + table_name + "` (" + ', '.join(columns) +
           ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" +
           " ON DUPLICATE KEY UPDATE " +
           ', '.join([c + ' = VALUES(' + c + ')' for c in columns]) +
           ", check_date_time = default;")  # data 시간을 확인시간과 비교하여 데이터가 완전히 수집되었는지 확인 가능
    try:
        cursor.executemany(sql, val)
    except pymysql.err.ProgrammingError:
        create_atpu_table(table_name)  # table 없는 경우 생성
        cursor.executemany(sql, val)
    conn.commit()


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
# run_atpu_insert(MARKET_ALL, '2022-02-01T00:00:00', '2022-02-11T14:00:00')
# run_atpu_insert(['KRW-WEMIX'], '2022-01-01T00:00:00', '2022-02-02T00:00:00')


def select_atpu(table_name, market, time_to):
    columns = ATPU_COLUMNS
    results = []
    sql = ("SELECT %s " % ', '.join(columns) +
           "FROM `test`.`%s`" % table_name +
           "WHERE (e_date_time < '%s' AND market = '%s')" % (time_to, market) +
           "ORDER BY e_date_time DESC LIMIT 1")
    try:
        cursor.execute(sql)
    except pymysql.err.ProgrammingError as e:
        print('pymysql error:', e.args[1])
        return results
    selected = cursor.fetchall()
    return selected
# select_atpu('atpu_2202', 'KRW-BTC', '2022-02-01 23:58:01')
# select_atpu('atpu_2202', 'KRW-BTC', datetime(2022, 2, 1, 23, 36))
# select_atpu('atpu_2202', 'KRW-BTC', datetime.now())


def get_atpu_seq(market, time_to_=False, count_=50):
    # DB sequential data select 시 table 접근 방법 설정 router 포함
    time_to = datetime.now() if not time_to_ else datetime_convert(time_to_, to_str=False)
    table_name = 'atpu_' + time_to.strftime("%y%m")
    results = []
    while len(results) < count_:
        sa = select_atpu(table_name, market, time_to)
        if not sa:
            # router 부분
            time_tmp = (time_to - timedelta(seconds=1)).replace(hour=0, minute=0, second=0)
            table_name = 'atpu_' + time_tmp.strftime("%y%m")
            if not check_table(table_name):
                return results
            continue
        results.extend(sa)
        time_to = datetime_convert(results[-1]['s_date_time'], to_str=False)
    return results[:count_]
# atpu_seq = get_atpu_seq('KRW-IQ', '2022-02-01T00:58:01')
# atpu_seq = get_atpu_seq('KRW-BTC')
# for a in atpu_seq:
#     print(a['e_date_time'], a['s_date_time'], a['duration'], a['mean_price'])
# market, time_to_, count_ = 'KRW-BTC', '2022-02-01T00:58:01', 50
# TODO: rawdata db 실시간 업데이트 구현 및 market view 수정(minutes(1, 10, 100): DB / day, week, month: API)


def run_insert_product_DB(market):
    # 기존 rawdata 확인
    time_to = datetime_convert(datetime.now())
    gdr = get_db_rawdata(market, count_=10)
    columns = ['market', 'candle_date_time_kst', 'check_date_time']
    for r in gdr:
        print(r['market'], r['candle_date_time_kst'])
        time_from = datetime_convert(r['candle_date_time_kst'], to_str=False)
        table_name = 'rawdata_' + time_from.strftime("%y%m")
        sql = ("SELECT %s " % ', '.join(columns) +
               "FROM `test`.`%s`" % table_name +
               "WHERE (candle_date_time_kst = '%s' AND market = '%s')" % (time_from, market))
        cursor.execute(sql)
        selected = cursor.fetchone()
        if selected['candle_date_time_kst'] < selected['check_date_time'] - timedelta(minutes=1):
            break
    run_rawdata_insert([market], s_time=datetime_convert(time_from), e_time=time_to)  # api to db
    run_atpu_insert([market], s_time=datetime_convert(time_from), e_time=time_to)  # TODO: 속도 문제로 따로 진행해야 함
    return

# run_insert_product_DB('KRW-BTC')
# while True:
#     for market in MARKET_ALL:
#         run_insert_product_DB(market)

