import os
from dotenv import load_dotenv

load_dotenv()

# Getting CSRF token
CSRF_PATH = "http://backend:8000/api/v1/get/csrf_token"
# CSRF_PATH = "http://185.233.119.84/api/v1/get/csrf_token"

# Creating user
USER_CREATION_PATH = "http://backend:8000/api/v1/user/create"
# USER_CREATION_PATH = "http://185.233.119.84/api/v1/user/create"

# Tg user
TG_USER = "http://backend:8000/api/v1/user/tg_user"

# Invoices
INVOICES_URL = "http://backend:8000/api/v1/invoice/set"

# ------------------------------- НАСТРОЙКИ ----------------------------------
# Токен бота из @BotFather. В проде лучше хранить в переменных окружения.
BOT_TOKEN = os.getenv("BOT_TOKEN")

API_SECRET_KEY = os.getenv("API_SECRET_KEY")

# Токен Crypto Pay API из @CryptoBot (Crypto Pay → Create App → Token).
CRYPTO_PAY_API_TOKEN = os.getenv("CRYPTO_PAY_API_TOKEN")

# Базовый URL Crypto Pay API (официальный).
CRYPTO_PAY_BASE = "https://pay.crypt.bot/api"

# Валюта для оплаты (например USDT/TON/BTC). Проверь поддержку в Crypto Pay.
ASSET = os.getenv("ASSET", "USDT")

# Контакт техподдержки (ник без @).
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "durak_ili_geniy")

# Отправлять ли файл после успешной оплаты (опционально).
SEND_FILE_ON_SUCCESS = os.getenv("SEND_FILE_ON_SUCCESS", "false").lower() == "true"

# ----------------------------- ТАРИФЫ/ПЛАНЫ ---------------------------------
# Как просили: 1м = $30, 3м = $50, 6м = $130.
TARIFFS = [
    {"code": "1m", "title": "1 месяц",  "amount": "15"},
    {"code": "3m", "title": "3 месяца", "amount": "30"},
    {"code": "12m", "title": "12 месяцев","amount": "90"},
]

# Быстрый поиск тарифа по code (для удобства).
TARIFFS_BY_CODE = {t["code"]: t for t in TARIFFS}