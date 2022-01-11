from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q, Count
from coinanser.models import TradeResults


def order_board(request):
    """
    order 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지

    # 정렬
    order_list = TradeResults.objects.order_by('-start_date_time')

    # 페이징처리
    paginator = Paginator(order_list, 20)  # 페이지당 20개씩 보여주기
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
    }

    return render(request, 'coinanser/order_board.html', context)
