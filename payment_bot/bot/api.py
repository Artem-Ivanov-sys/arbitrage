import requests
import aiohttp

from .constants import CRYPTO_PAY_API_TOKEN, ASSET, CRYPTO_PAY_BASE, CSRF_PATH, USER_CREATION_PATH, API_SECRET_KEY, TG_USER, INVOICES_URL

def mdv2_escape(text: str) -> str:
    """Экранирует служебные символы MarkdownV2 (Telegram)."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    result = ""
    for ch in text:
        result += ("\\" + ch) if ch in escape_chars else ch
    return result

async def get_user_info(user_name, months):
    async with aiohttp.ClientSession() as session:
        async with session.get(CSRF_PATH) as resp:
            csrftoken = resp.cookies.get('csrftoken').value

        async with session.post(USER_CREATION_PATH, data={"user_name": user_name, "months": months}, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-KEY': API_SECRET_KEY,
            'X-CSRFToken': csrftoken}, cookies={"csrftoken": csrftoken}) as resp:
            j = await resp.json()

            login_text = (
                mdv2_escape("Login data:") + "\n\n"
                + mdv2_escape("Login:") + "\n"
                + "```\n" + mdv2_escape(f"{j['username']}") + "\n```\n\n"
                + mdv2_escape("Password:") + "\n"
                + "```\n" + mdv2_escape(f"{j['password']}") + "\n```\n"
                + mdv2_escape("Thank you for paid! 🥰")
            )

            return login_text

async def save_invoice(**kwargs):
    data = dict(keys=['uid', 'user_tg_id', 'pay_amount', 'pay_status', 'tariff'], values=[kwargs.get(i, None) for i in ['uid', 'user_tg_id', 'pay_amount', 'pay_status', 'tariff']])
    async with aiohttp.ClientSession() as session:
        async with session.get(CSRF_PATH) as resp:
            csrftoken = resp.cookies.get('csrftoken').value

        async with session.post(INVOICES_URL, data=data, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-KEY': API_SECRET_KEY,
            'X-CSRFToken': csrftoken}, cookies={"csrftoken": csrftoken}) as resp:

            return await resp.json()

async def save_tg_user(tg_user_id, username):
    async with aiohttp.ClientSession() as session:
        async with session.get(CSRF_PATH) as resp:
            csrftoken = resp.cookies.get('csrftoken').value

        async with session.post(TG_USER, data={"tg_user_id": tg_user_id, "username": username}, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-KEY': API_SECRET_KEY,
            'X-CSRFToken': csrftoken}, cookies={"csrftoken": csrftoken}) as resp:

            return await resp.json()

async def get_tg_user(tg_user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(CSRF_PATH) as resp:
            csrftoken = resp.cookies.get('csrftoken').value

        async with session.get(TG_USER, data={"tg_user_id": tg_user_id}, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-KEY': API_SECRET_KEY,
            'X-CSRFToken': csrftoken}, cookies={"csrftoken": csrftoken}) as resp:

            return await resp.json()

# ------------------------------ УТИЛИТЫ API ---------------------------------
def crypto_headers():
    """Заголовки для Crypto Pay API (токен обязателен)."""
    return {"Crypto-Pay-API-Token": CRYPTO_PAY_API_TOKEN}

def create_invoice(amount: str, asset: str = ASSET, description: str = None):
    """
    Создать инвойс в Crypto Pay и вернуть (pay_url, invoice_id) либо (None, None).
    Документация: createInvoice.
    """
    data = {"asset": asset, "amount": amount}
    if description:
        data["description"] = description
    try:
        resp = requests.post(f"{CRYPTO_PAY_BASE}/createInvoice",
                             headers=crypto_headers(),
                             json=data,
                             timeout=15)
    except requests.RequestException as e:
        print(f"[create_invoice] Ошибка запроса: {e}")
        return None, None

    if resp.ok:
        j = resp.json()
        if j.get("ok") and "result" in j:
            res = j["result"]
            pay_url = res.get("pay_url")
            invoice_id = res.get("invoice_id")
            if pay_url and invoice_id is not None:
                return str(pay_url), str(invoice_id)

    print(f"[create_invoice] Не удалось создать инвойс. Ответ: {resp.text}")
    return None, None

def get_invoice_status(invoice_id: str):
    """Получить статус инвойса по id. Возвращает json либо None."""
    params = {"invoice_ids": invoice_id}
    try:
        resp = requests.get(f"{CRYPTO_PAY_BASE}/getInvoices",
                            headers=crypto_headers(),
                            params=params,
                            timeout=15)
    except requests.RequestException as e:
        print(f"[get_invoice_status] Ошибка запроса: {e}")
        return None

    if resp.ok:
        j = resp.json()
        if j.get("ok"):
            return j
    print(f"[get_invoice_status] Не удалось получить статус. Ответ: {resp.text}")
    return None