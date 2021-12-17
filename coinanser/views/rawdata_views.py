from django.shortcuts import render, get_object_or_404
from coinanser.models import RawdataKrwAda
# import json

def select_test(request):
    # rawdata = RawdataKrwAda.objects.order_by('-date_time')[0:50]
    rawdata = RawdataKrwAda.objects.all()[0:200]
    test = RawdataKrwAda.objects.all()[0:10]
    context = {
        # 'data_set': [
        #     [1,  37.8, 80.8, 41.8],
        #     [2, 30.9, 69.5, 32.4],
        #     [3, 25.4, 57, 25.7],
        #     [4, 11.7, 18.8, 10.5],
        # ],
        'rawdata': rawdata,
        'test': test,
    }
    # return render(request, 'google_chart/linechart_material.html', {'contextJson': json.dumps(context)})
    return render(request, 'google_chart/test.html', context)





