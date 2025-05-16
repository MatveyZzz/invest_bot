from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import asyncio
import os
from dotenv import load_dotenv

from grathics import generate_stock_chart
from data_manage import add_data, get_data, delete_data, update_user, check_subscription
from finance_info import company_search, get_time_series
import config
from bot_actions import search_n_select_company, reset_user, send_real_time_data
from data_manage import get_data, get_company_id

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


# --- Меню клавиатур ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("Получить информацию об акциях компании 📈", callback_data="get_stock_info")],
        [InlineKeyboardButton("Обновить информацию 🔄 (не работает)", callback_data="update_stock_info")],
        [InlineKeyboardButton("Краткая сводка 📋(Не работает)", callback_data="market_summary")],
        [InlineKeyboardButton("Настройки ⚙️", callback_data="settings_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_menu():
    keyboard = [
        [InlineKeyboardButton("Настройка отслеживаемых компаний(Нет)", callback_data="manage_companies")],
        [InlineKeyboardButton("Выбрать количество рассылок в день(Нет)", callback_data="set_mail_count")],
        [InlineKeyboardButton("Выбрать время рассылок(Нет)", callback_data="set_mail_time")],
        [InlineKeyboardButton("Включить/выключить ежедневную рассылку(Нет)", callback_data="toggle_subscription")],
        [InlineKeyboardButton("Сброс данных 🗑️", callback_data="reset_data")],
        [InlineKeyboardButton("Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Здесь можно добавить другие меню, например для управления компаниями, выбора времени и т.д.

# --- Хранилище пользователей (вместо БД) ---
users_data = {}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "companies": [],
            "subscription": False,
            "requests_today": 0,
            "mail_count": 1,      # количество рассылок в день
            "mail_times": []       # список часов отправки (формат "HH:MM")
        }
    return users_data[user_id]

# --- Обработчики ---
async def start(update: Update, context):
    user = update.effective_user
    user_id = user.id
    await add_data('Users', user_id)
    await update_user(user_id, 'status', 'Idle')
    #get_user_data(user_id)
    await update.message.reply_text(
        "Привет! Я бот для получения информации о фондовом рынке.",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    #user_data = get_user_data(user_id)

    if data == "get_stock_info":
        # Вызов: начать диалог поиска компании
        await query.message.reply_text("Введите уникальный Ticker-символ компании для начала поиска 🔎:")
        await update_user(user_id, 'status', 'TICKER_AWAIT')

    # elif data == "update_stock_info":
    #     reqs_left = int((await get_data('Users', 'info_requests', 'user_tg_id', user_id))[0][0])
    #     if reqs_left > 0:
    #         companies_tasks = []
    #         for company in await get_data('LinkTable', 'company_id', 'user_tg_id', user_id):

        

    elif data == "market_summary":
        # Вызов: сгенерировать краткую сводку через ИИ
        await query.message.reply_text("Генерация краткой сводки...")

    elif data == "settings_menu":
        # Показать меню настроек
        await query.message.reply_text("Меню настроек:", reply_markup=settings_menu())

    elif data == "manage_companies":
        # Вызов: показать/добавить/удалить отслеживаемые компании
        await query.message.reply_text("Здесь будет меню управления компаниями.")

    elif data == "set_mail_count":
        # Вызов: установить количество рассылок в день
        await query.message.reply_text("Введите, сколько раз в день вы хотите получать рассылку (число):")

    elif data == "set_mail_time":
        # Вызов: установить время рассылок
        await query.message.reply_text("Введите время рассылки в формате HH:MM. Для нескольких — через запятую:")

    # elif data == "toggle_subscription":
    #     # Вызов: включить/выключить ежедневную рассылку
    #     user_data["subscription"] = not user_data["subscription"]
    #     status = "включена" if user_data["subscription"] else "выключена"
    #     await query.message.reply_text(f"Ежедневная рассылка {status}.")

    elif data == "reset_data":
        # Вызов: сброс данных пользователя
        await reset_user(user_id)
        await query.message.reply_text("Ваши данные сброшены.", reply_markup=main_menu())

    elif data == "back_to_main":
        # Вернуться в главное меню
        await update_user(user_id, 'status', 'Idle')
        await query.message.reply_text("Главное меню:", reply_markup=main_menu())

    elif data.startswith('Found_companies:'):
        data = data.split(':')[1:]
        additional_data = ''
        keyboard = []
        sub_status = await check_subscription(user_id, data[1], data[2])
        print(sub_status)
        if not sub_status:
            keyboard.append([InlineKeyboardButton('Подписаться', callback_data=f'AddCompany:{data[0]}:{data[1]}:{data[2]}')])
        else:
            additional_data = 'Вы подписаны ✅'
        keyboard.append([InlineKeyboardButton('Вернуться в меню', callback_data='back_to_main')])

        result = await get_time_series(data[1], data[2], config.FIN_DATA_INTERVAL, config.FIN_DATA_OUTPUTS)
        await query.edit_message_text(text=f'Изменения цен на акции "{data[0]}" за последнюю неделю.\n' + additional_data,
                                      reply_markup=InlineKeyboardMarkup(keyboard))

        #Вызов отрисовки графика изменения цены на акции выбранной компании
        await send_real_time_data(result, update, context)
    
    elif data.startswith('AddCompany:'):
        data = data.split(':')[1:]
        company_id = await get_company_id(data[1], data[2])
        if not company_id:
            await add_data('Companies', data[0], data[1], data[2])
            company_id = await get_company_id(data[1], data[2])
        subs = (await get_data('Users', 'following', 'user_tg_id', user_id))[0]
        if subs[0] < config.SUBSCRIPTIONS_LIMIT:
            asyncio.gather(add_data('LinkTable', user_id, company_id), update_user(user_id, 'following', subs[0] + 1))
            answer =  'Вы успешно подписались!'
        elif subs[0] >= config.SUBSCRIPTIONS_LIMIT:
            answer = 'Вы превысили количество активных подписок ❌'
        else:
            answer = 'Неизвестная ошибка.'
        await query.message.reply_text(answer)

    else:
        await query.message.reply_text("Неизвестная команда.")

# Обработчики обычных сообщений (для ввода количества рассылок, времени и поиска)
async def text_handler(update: Update, context):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    text = update.message.text

    status = (await get_data('Users', 'status', 'user_tg_id', user_id))[0]

    if status[0] == 'TICKER_AWAIT':
        result = await search_n_select_company(text)
        if result == -1:
            await update.message.reply_text("По вашему запросу ничего не нашлось.")
        else:
            await update.message.reply_text('Вот, что удалось найти по вашему запросу:', reply_markup=result)
        

    # # Пример: если пользователь вводит число рассылок
    # if text.isdigit():
    #     user_data["mail_count"] = int(text)
    #     await update.message.reply_text(f"Установлено {text} рассылок в день.")
    #     return

    # # Пример: если пользователь вводит время рассылок
    # if ":" in text:
    #     times = [t.strip() for t in text.split(",")]
    #     user_data["mail_times"] = times
    #     await update.message.reply_text(f"Установлено время рассылки: {', '.join(times)}.")
    #     return

    # # Другие тексты: например, поиск компании
    # await update.message.reply_text("Обрабатываю ввод...")

# --- Точка входа ---
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Бот запущен...")
    app.run_polling()
