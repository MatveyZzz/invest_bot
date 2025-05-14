from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "YOUR_BOT_TOKEN"

# --- Меню клавиатур ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("Получить информацию об акциях компании", callback_data="get_stock_info")],
        [InlineKeyboardButton("Обновить информацию", callback_data="update_stock_info")],
        [InlineKeyboardButton("Краткая сводка", callback_data="market_summary")],
        [InlineKeyboardButton("Настройки", callback_data="settings_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_menu():
    keyboard = [
        [InlineKeyboardButton("Настройка отслеживаемых компаний", callback_data="manage_companies")],
        [InlineKeyboardButton("Выбрать количество рассылок в день", callback_data="set_mail_count")],
        [InlineKeyboardButton("Выбрать время рассылок", callback_data="set_mail_time")],
        [InlineKeyboardButton("Включить/выключить ежедневную рассылку", callback_data="toggle_subscription")],
        [InlineKeyboardButton("Сброс данных", callback_data="reset_data")],
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
    # TODO: добавить пользователя в базу данных
    get_user_data(user_id)
    await update.message.reply_text(
        "Привет! Я бот для получения информации о фондовом рынке.",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    if data == "get_stock_info":
        # Вызов: начать диалог поиска компании
        await query.message.reply_text("Введите название компании:")

    elif data == "update_stock_info":
        # Вызов: обновить информацию по отслеживаемым компаниям
        if user_data["requests_today"] >= 3:
            await query.message.reply_text("Вы достигли лимита обновлений на сегодня.")
        else:
            user_data["requests_today"] += 1
            await query.message.reply_text("Обновляем информацию...")

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

    elif data == "toggle_subscription":
        # Вызов: включить/выключить ежедневную рассылку
        user_data["subscription"] = not user_data["subscription"]
        status = "включена" if user_data["subscription"] else "выключена"
        await query.message.reply_text(f"Ежедневная рассылка {status}.")

    elif data == "reset_data":
        # Вызов: сброс данных пользователя
        users_data.pop(user_id, None)
        await query.message.reply_text("Ваши данные сброшены.", reply_markup=main_menu())

    elif data == "back_to_main":
        # Вернуться в главное меню
        await query.message.reply_text("Главное меню:", reply_markup=main_menu())

    else:
        await query.message.reply_text("Неизвестная команда.")

# Обработчики обычных сообщений (для ввода количества рассылок, времени и поиска)
async def text_handler(update: Update, context):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    text = update.message.text

    # Пример: если пользователь вводит число рассылок
    if text.isdigit():
        user_data["mail_count"] = int(text)
        await update.message.reply_text(f"Установлено {text} рассылок в день.")
        return

    # Пример: если пользователь вводит время рассылок
    if ":" in text:
        times = [t.strip() for t in text.split(",")]
        user_data["mail_times"] = times
        await update.message.reply_text(f"Установлено время рассылки: {', '.join(times)}.")
        return

    # Другие тексты: например, поиск компании
    await update.message.reply_text("Обрабатываю ввод...")

# --- Точка входа ---
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Бот запущен...")
    app.run_polling()
