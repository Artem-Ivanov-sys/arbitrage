from django.urls import path
from .views import getFundingsView, createUserView, authorizeView, getCSRFTokenView, TgUserView, InvoiceView, getUserView, logoutView, getUserView

urlpatterns = [
    path('get/', getFundingsView),                     # Отримання даних з бірж
    path('get/user', getUserView),                     # Отримати ім'я користувача
    path('get/csrf_token', getCSRFTokenView),          # Отримання CSRF токену
    path('user/tg_user', TgUserView),                  # Додавання/зміна/отримання тг юзера
    path('user/create', createUserView),               # Створення юзера
    path('user/login', authorizeView),                 # Логін юзера
    path('user/logout', logoutView),                   # Логаут юзера
    path('user/whoami', getUserView),                  # Отримання поточного юзера
    path('invoice/set', InvoiceView)                   # Додавання/зміна інвойса
]
