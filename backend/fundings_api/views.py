# from django.shortcuts import render
from .models import MainFundingModel
from django.http import JsonResponse, HttpResponse
from json import loads
from django.contrib.auth.models import User
from random import choice
from string import ascii_letters, digits
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.serializers import serialize
from django.forms.models import model_to_dict

# Create your views here.

def getCSRFTokenView(request):
    if request.method == "GET":
        return JsonResponse({})
    return JsonResponse({"error": "GET required"})

def createUserView(request):
    def generate_username(length):
        return f"{request.POST.get('user_name')}_{''.join([choice(ascii_letters+digits) for i in range(length)])}"
    def generate_password(length):
        return f"{''.join([choice(ascii_letters+digits+"_") for i in range(length)])}"
    
    if request.method == "POST":
        if request.POST.get('user_name'):
            username=generate_username(10)
            password=generate_password(20)
            user = User.objects.create_user(username=username, password=password)
            user.save()
            return JsonResponse({"username": user.username, "password": password})
        return JsonResponse({"error": "user_name is empty"})
    return JsonResponse({"error": "POST required"})

def authorizeView(request):
    if request.method == "GET":
        users = User.objects.values("id", "username", "password")
        return JsonResponse(list(users), safe=False)
    else:
        return JsonResponse({"error": "GET required"})

@ensure_csrf_cookie
def getFundingsView(request):
    print(request.META['REMOTE_ADDR'])
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "localhost, http://185.103.101.172"
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
                    }
                )
    return_data['coins'].sort(key=lambda x: x['long']['rate']-x['short']['rate'], reverse=True)
    return JsonResponse(return_data, safe=False)
