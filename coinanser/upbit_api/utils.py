from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint


def datetime_convert(time_, to_str=True, to_utc=False, sec_delta=0, month_delta=0):
    # 시간 변환 (type(time_): str or datetime or int)
    if type(time_) == str:
        dtime = datetime.strptime(time_, '%Y-%m-%dT%H:%M:%S')
    if type(time_) == int:
        dtime = datetime.fromtimestamp(time_/1000)
    if type(time_) == datetime:
        dtime = time_

    if month_delta:
        month_change = relativedelta(months=month_delta)
        ymd = dtime.date() + month_change
        dtime = dtime.replace(year=ymd.year, month=ymd.month)

    time_change = timedelta(seconds=sec_delta)
    if to_utc:
        time_change += timedelta(hours=-9)  # api query는 utc 기준으로 입력되어야 함
    dtime = dtime + time_change

    # 타입 변환
    if to_str:
        str_time_tmp = str(dtime).split('.')[0]
        str_time = 'T'.join(str_time_tmp.split())
        return str_time

    return dtime

