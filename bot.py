from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "YOUR_BOT_TOKEN"

# Главное меню
def main_menu():
    keyboard = [
        [InlineKeyboardButton("Получить информацию об акциях компании", callback_data="get_stock_info")],
        [InlineKeyboardButton("Обновить информацию", callback_data="update_stock_info")],
        [InlineKeyboardButton("Краткая сводка", callback_data="market_summary")],
        [InlineKeyboardButton("Настройки", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Хранилище пользователей
users_data = {}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {"companies": [], "subscription": False, "requests_today": 0}
    return users_data[user_id]

async def start(update: Update, context):
    user_data = get_user_data(update.effective_user.id)
    await update.message.reply_text("Привет! Я бот для получения информации о фондовом рынке.", reply_markup=main_menu())

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "get_stock_info":
        await query.message.reply_text("Введите название компании:")
    elif query.data == "update_stock_info":
        user_data = get_user_data(update.effective_user.id)
        if user_data["requests_today"] >= 3:
            await query.message.reply_text("Вы достигли лимита обновлений на сегодня.")
        else:
            user_data["requests_today"] += 1
            await query.message.reply_text("Обновляем информацию...")
    elif query.data == "market_summary":
        await query.message.reply_text("Генерация краткой сводки...")
    elif query.data == "settings":
        await query.message.reply_text("Настройки пока недоступны.")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Бот запущен...")
    app.run_polling()
