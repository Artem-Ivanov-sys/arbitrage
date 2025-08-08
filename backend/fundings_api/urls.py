from django.urls import path
from .views import getFundingsView, createUserView, authorizeView, getCSRFTokenView

urlpatterns = [
    path('get/', getFundingsView),
    path('user/create', createUserView),
    path('user/login', authorizeView),
    path('get/csrf_token', getCSRFTokenView)
]
