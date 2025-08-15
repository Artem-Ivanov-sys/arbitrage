# from django.shortcuts import render
from .models import MainFundingModel
from django.http import JsonResponse, HttpResponseForbidden
from json import loads
from random import choice
from string import ascii_letters, digits
from django.views.decorators.csrf import ensure_csrf_cookie
# from django.core.serializers import serialize
# from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from .models import UserModel, TgUserModel, PaymentModel
from django.contrib.auth import authenticate, login, get_user_model
from datetime import timedelta
from django.utils import timezone
from .forms import LoginForm
from os import getenv
from django.contrib.auth.models import User

# Create your views here.

@ensure_csrf_cookie
def getCSRFTokenView(request):
    if request.method == "GET":
        return JsonResponse({})
    return JsonResponse({"error": "GET required"})

def InvoiceView(request):
    if request.headers.get("X-API-KEY") != getenv("API_SECRET_KEY"):
        return HttpResponseForbidden("Invalid key")
    if request.method == "POST":
        data = dict(keys=['uid', 'user_tg_id', 'pay_amount', 'pay_status', 'tariff'], values=[request.POST.get(i, None) for i in ['uid', 'user_tg_id', 'pay_amount', 'pay_status', 'tariff']])
        data['status'] = ["Active", "Paid", "Expired"].index(data.get("status"))+1

        if invoice:=PaymentModel.objects.all().filter(uid=data.get("uid")).first():
            invoice.status = data.get("status")
        else:
            PaymentModel.objects.create(**data)
        return JsonResponse({"status": True})

    return JsonResponse({"status": False, "error": "POST required"})

def TgUserView(request):
    if request.headers.get("X-API-KEY") != getenv("API_SECRET_KEY"):
        return HttpResponseForbidden("Invalid key")
    if request.method == "GET":
        tg_user_id = request.GET.get("tg_user_id")
        if not tg_user_id:
            return JsonResponse({"error": "tg_user_id is required"}, status=400)

        query = TgUserModel.objects.all().filter(tg_user_id=tg_user_id).first()
        if query:
            return JsonResponse({"username": query.username})
        else:
            return JsonResponse({"error": "user doesn't exist"})
    elif request.method == "POST":
        tg_user_id = request.POST.get("tg_user_id")
        username = request.POST.get("username")
        if not tg_user_id or not username:
            return JsonResponse({"error": "tg_user_id and username are required"}, status=400)

        query = TgUserModel.objects.all().filter(tg_user_id=tg_user_id).first()
        if query:
            query.username = username
            query.save()
        else:
            query = TgUserModel.objects.create(tg_user_id=tg_user_id, username=username)
        return JsonResponse({"username": query.username})
    else:
        return JsonResponse({"error": "unexpected request method"}, status=405)

def createUserView(request):
    if request.headers.get("X-API-KEY") != getenv("API_SECRET_KEY"):
        return HttpResponseForbidden("Invalid key")
    def generate_username(length):
        if request.POST.get('user_name') is None:
            return f"{request.POST.get('user_name')}_{''.join([choice(ascii_letters+digits) for i in range(length)])}"
        while True:
            if not User.objects.all().filter(username=(username:=''.join([choice(ascii_letters+digits) for i in range(length)]))).first():
                return username
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
                    if timezone.now() < user.user_data.user_subscription_expire or user.user_subscription_level == "admin":
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
