# from django.shortcuts import render
from .models import MainFundingModel
from django.http import JsonResponse, HttpResponse
from json import loads
# from django.contrib.auth.models import User
from random import choice
from string import ascii_letters, digits
from django.views.decorators.csrf import ensure_csrf_cookie
# from django.core.serializers import serialize
# from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from .models import UserModel
from django.contrib.auth import authenticate, login, get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from .forms import LoginForm
from django.shortcuts import redirect

# Create your views here.

@ensure_csrf_cookie
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
            user = get_user_model().objects.create_user(
                username=username,
                password=password
            )
            user_ = UserModel.objects.create(
                user=user,
                user_tg_id=0,
                user_subscription_level='regular',
                user_subscription_expire=timezone.now() + timedelta(days=30)
            )
            return JsonResponse({"username": username, "password": password})
        return JsonResponse({"error": "user_name is empty"})
    return JsonResponse({"error": "POST required"})

def authorizeView(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        print(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    if timezone.now() < user.user_data.user_subscription_expire:
                        login(request, user)
                        return JsonResponse({'redirect_url': '/'})
                    else:
                        return JsonResponse({"error": "Subscription expired"})
                else:
                    return JsonResponse({"error": "User is inactive"})
            else:
                return JsonResponse({"error": "Login failed"})
        else:
            return JsonResponse({"error": "Invalid form"})
    else:
        return JsonResponse({"error": "POST required"})

@login_required
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
