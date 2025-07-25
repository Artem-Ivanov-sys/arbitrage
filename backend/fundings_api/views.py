# from django.shortcuts import render
from .models import MainFundingModel
from django.http import JsonResponse
from json import loads

# Create your views here.
def getFundingsView(request):
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, ngrok-skip-browser-warning"
        return response
    
    data = MainFundingModel.objects.all().order_by('-time').first()
    return_data = {
        'time': data.time,
        'coins': [

        ]
    }

    const_time = {
        'backpack': 8,
        'kiloex': 1,
        'aevo': 1,
        'paradex': 8
    }

    for coin in data['fundings']:
        if len(data['fundings'][coin]) > 1:
            '''
            # TODO: переписати логіку, щоб повертались всі монети, а на фронті окремо формувати комбінації бірж
            в залежності від того, чи по фандінгу чи по спреду сортуємо, бо ця логіка не враховує, що можуть бути
            комбінації з більшим спредом по ціні, але меншим по фандінгу
            '''
            keys = data['fundings'][coin].keys()
            max_ = ['', -100000]
            min_ = ['', 100000]
            for i in keys:
                if data['fundings'][coin][i]['index_price'] == 0:
                    continue
                if data['fundings'][coin][i]['rate'] > max_[1]:
                    max_ = [i, data['fundings'][coin][i]['rate'], data['fundings'][coin][i]['index_price'], data['fundings'][coin][i]['reset_time']]
                if data['fundings'][coin][i]['rate'] < min_[1]:
                    min_ = [i, data['fundings'][coin][i]['rate'], data['fundings'][coin][i]['index_price'], data['fundings'][coin][i]['reset_time']]
            
            if min_[0] != max_[0]:
                return_data['coins'].append(
                    {
                        'coin': coin,
                        'long': {
                            'exchange': max_[0],
                            'rate': max_[1],
                            'index_price': max_[2],
                            'reset_time': max_[3]
                        },
                        'short': {
                            'exchange': min_[0],
                            'rate': min_[1],
                            'index_price': min_[2],
                            'reset_time': min_[3]
                        },
                        # 'delta': (max_[1] - min_[1])*100,

                        # 'APR': ((max_[1] * (24 / const_time[max_[0]]) ) - (min_[1] / (24 / const_time[min_[0]]) )) * 8760,
                        
                        # 'spread': abs(max_[2]-min_[2])/max(max_[2], min_[2])*100 if max(max_[2], min_[2]) else -1
                    }
                )
            else:
                print(data['fundings'][coin])
    return_data['coins'].sort(key=lambda x: x['long']['rate']-x['short']['rate'], reverse=True)
    return JsonResponse(return_data, safe=False)
