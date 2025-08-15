# -*- coding: utf-8 -*-
# ============================================================================
# bot_v6.1.py
# ----------------------------------------------------------------------------
# Телеграм-бот (pyTelegramBotAPI / TeleBot) + Crypto Pay API (@CryptoBot).
# Что умеет:
#   • /start — приветствие + кнопка «Оплатить».
#   • По нажатию «Оплатить» показывает ТРИ ТАРИФА (кнопки).
#   • Пользователь выбирает тариф → БОТ СОЗДАЁТ РОВНО ОДИН инвойс.
#   • Отправляем 2 кнопки: «Оплатить» (URL) и «Проверить оплату» (для ЭТОГО одного инвойса).
#   • /support — команда техподдержки (контакт).
#   • Проверка статуса через getInvoices; при 'paid' — выдаём доступ.
# ВАЖНО: Максимально подробные комментарии, чтобы удобно дебажить.
# ============================================================================

# import os                                   # переменные окружения (токены и т.п.)
# import requests                             # HTTP-запросы к Crypto Pay API
import telebot                              # библиотека для Телеграм-бота
from telebot import types                   # кнопки, клавиатуры и т.д.
import asyncio

from .api import get_invoice_status, create_invoice, get_user_info, save_tg_user, get_tg_user, save_invoice
from .constants import BOT_TOKEN, SUPPORT_USERNAME, TARIFFS, ASSET, TARIFFS_BY_CODE

# --------------------------- ИНИЦИАЛИЗАЦИЯ БОТА -----------------------------
bot = telebot.TeleBot(BOT_TOKEN)           # создаём экземпляр бота

# Память последнего счёта для каждого чата:
# last_invoice[chat_id] = {"invoice_id": "123", "title": "1 месяц", "amount": "30"}
last_invoice = {}

# ------------------------------ КОМАНДЫ БОТА ---------------------------------
@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message):
    """Команда /start — приветствие + кнопка «Оплатить» (открывает выбор тарифов)."""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="Оплатить", callback_data="open_tariffs"))
    asyncio.run(save_tg_user(message.from_user.id, message.from_user.username))
    bot.send_message(
        message.chat.id,
        "Добро пожаловать! Нажмите «Оплатить», выберите тариф и оформите подписку.",
        reply_markup=kb
    )

@bot.message_handler(commands=['support'])
def cmd_support(message: types.Message):
    """Команда /support — контакт поддержки."""

    if SUPPORT_USERNAME:
        text = f"Техподдержка: @{SUPPORT_USERNAME}\nУкажите ваш ID: {message.from_user.id}"
    else:
        text = "Техподдержка временно недоступна."
    bot.send_message(message.chat.id, text)

# ------------------------------ КОЛЛБЭКИ ------------------------------------
@bot.callback_query_handler(func=lambda c: c.data == "open_tariffs")
def cb_open_tariffs(call: types.CallbackQuery):
    """Показать три тарифа (кнопки выбора)."""
    kb = types.InlineKeyboardMarkup(row_width=1)
    # Для каждого тарифа делаем кнопку «Выбрать: ...» с callback_data вида choose_1m/3m/6m.
    for t in TARIFFS:
        kb.add(types.InlineKeyboardButton(
            text=f"Выбрать: {t['title']} — {t['amount']} {ASSET}",
            callback_data=f"choose_{t['code']}"
        ))
    bot.edit_message_text(  # редактируем предыдущее сообщение с «Оплатить»
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите тариф:",
        reply_markup=kb
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("choose_"))
def cb_choose_tariff(call: types.CallbackQuery):
    """
    Пользователь выбрал тариф → создаём РОВНО ОДИН инвойс,
    сохраняем его как last_invoice для чата и отправляем две кнопки:
    - «Оплатить» (URL)
    - «Проверить оплату» (callback)
    """
    chat_id = call.message.chat.id
    code = call.data.split("choose_")[1]      # достаём '1m'/'3m'/'6m'
    tariff = TARIFFS_BY_CODE.get(code)        # ищем тариф по коду
    if not tariff:
        bot.answer_callback_query(call.id, "Тариф не найден.", show_alert=True)
        return

    title = tariff["title"]
    amount = tariff["amount"]

    # Создаём инвойс только на выбранный тариф.
    pay_url, invoice_id = create_invoice(amount=amount, asset=ASSET, description=f"Тариф: {title}")
    if not pay_url or not invoice_id:
        bot.answer_callback_query(call.id, "Ошибка: не удалось создать счёт.", show_alert=True)
        return

    # Сохраняем «последний инвойс» для этого чата.
    last_invoice[chat_id] = {"invoice_id": invoice_id, "title": title, "amount": amount}

    # Собираем клавиатуру с двумя кнопками.
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=f"Оплатить — {title} ({amount} {ASSET})", url=pay_url))
    kb.add(types.InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment"))

    # Отправляем сообщение с кнопками.
    bot.send_message(
        chat_id,
        f"Счёт создан для тарифа: {title} ({amount} {ASSET}).\n"
        f"Нажмите «Оплатить», затем «Проверить оплату».",
        reply_markup=kb
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "check_payment")
def cb_check_payment(call: types.CallbackQuery):
    print(call.from_user.username)
    """
    Проверяем оплату ТОЛЬКО для «последнего инвойса» в этом чате.
    Удобно и не путает пользователя несколькими счетами.
    """
    chat_id = call.message.chat.id
    info = last_invoice.get(chat_id)
    print(info)
    #bot.send_message(chat_id, info, parse_mode="MarkdownV2")

    if not info:
        bot.answer_callback_query(call.id, "Нет активного счёта для проверки.", show_alert=True)
        return

    invoice_id = info["invoice_id"]
    status_json = get_invoice_status(invoice_id)
    if not status_json or not status_json.get("ok"):
        bot.answer_callback_query(call.id, "Ошибка при получении статуса оплаты.", show_alert=True)
        return

    items = status_json.get("result", {}).get("items", [])
    inv = next((x for x in items if str(x.get("invoice_id")) == str(invoice_id)), None)

    if not inv:
        bot.answer_callback_query(call.id, "Счёт не найден.", show_alert=True)
        return

    status = str(inv.get("status", "")).lower()

    if status == "paid":

        #TODO когда юзер оплатил, ответ бота идёт в виде такого текста

        # Успех: отправляем доступ, optionally файл.
        bot.send_message(chat_id, "Оплата прошла успешно ✅")


        months = int(last_invoice[chat_id].get('title').split()[0])
        bot.send_message(chat_id, asyncio.run(get_user_info(None, months=months)), parse_mode="MarkdownV2")


        bot.send_message(chat_id, "Сайт: http://185.233.119.84")


        # Чистим last_invoice, чтобы не проверять старый счёт.
        last_invoice.pop(chat_id, None)

        bot.answer_callback_query(call.id)

    elif status == "active":
        bot.answer_callback_query(call.id, "Оплата не найдена ❌ (счёт активен)", show_alert=True)
    else:
        bot.answer_callback_query(call.id, f"Статус счёта: {status}", show_alert=True)

# ------------------------------- ЗАПУСК --------------------------------------
if __name__ == "__main__":
    print("Bot v5 is running (long polling). Press Ctrl+C to stop.")
    bot.infinity_polling(skip_pending=True, timeout=30)
