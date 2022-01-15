from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q, Count, Sum
from coinanser.models import TradeResults
from coinanser.upbit_api.utils import datetime_convert
from datetime import datetime, timedelta


def order_board(request):
    """
    order 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지

    # 정렬
    order_list = TradeResults.objects.order_by('-start_date_time')

    # 필터 (전체 / 모델버전 / 마켓명 등)

    # 날짜별 요약
    s_datetime = datetime.combine(order_list.last().start_date_time.date(), datetime.min.time())
    e_datetime = datetime.combine(order_list.first().start_date_time.date(), datetime.min.time())
    summary_list = []
    while s_datetime <= e_datetime:
        summary = {'date': datetime_convert(s_datetime)}
        query_set = order_list.filter(start_date_time__gte=s_datetime,  # >=
                                      start_date_time__lt=s_datetime + timedelta(days=1))  # <
        query_set = query_set.exclude(ask_date_time__isnull=True)
        summary['count'] = query_set.count()
        summary.update(query_set.aggregate(Sum('bid_funds'), Sum('ask_funds')))
        if summary['count']:
            summary['rev_funds'] = summary['ask_funds__sum'] - summary['bid_funds__sum']
            summary['rev_ratio'] = summary['rev_funds'] / summary['bid_funds__sum']
            summary['tooltip'] = ('수익금액: ' + str(format(round(summary['rev_funds']), ',')) + '원' +
                                  '\\n거래횟수: ' + str(round(summary['count'])) + '건' +
                                  '\\n매수금액: ' + str(format(round(summary['bid_funds__sum']), ',')) + '원' +
                                  '\\n매도금액: ' + str(format(round(summary['ask_funds__sum']), ',')) + '원' +
                                  '\\n수익률: ' + str(round(summary['rev_ratio'] * 100, 2)) + '%')
        else:
            summary['rev_funds'] = 0
            summary['rev_ratio'] = 0
            summary['tooltip'] = None

        summary_list.append(summary)
        s_datetime += timedelta(days=1)
    order_last = datetime_convert(query_set.first().ask_date_time, to_str=False).strftime("%Y/%m/%d %H:%M:%S")
    # 페이징처리
    paginator = Paginator(order_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    page_len = paginator.num_pages
    page_start = max(1, page_obj.number - max(2, page_obj.number - page_len + 4))
    page_end = min(page_len, page_obj.number + max(2, 5 - page_obj.number))

    context = {
        'order_list': page_obj,
        'order_list_len': page_len,
        'page_start': page_start,
        'page_end': page_end,
        'page': page,
        'summary_list': summary_list,
        'order_last': order_last
    }

    return render(request, 'coinanser/order_board.html', context)
