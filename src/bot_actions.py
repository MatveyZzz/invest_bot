from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import ContextTypes
import asyncio

import config
from finance_info import company_search
from data_manage import delete_data, update_user
from grathics import generate_stock_chart

async def send_image_local(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    with open("stock_chart.png", 'rb') as photo_file:
        await context.bot.send_photo(chat_id=chat_id, photo=InputFile(photo_file))

async def search_n_select_company(text):
    search_result = await company_search(text, config.SEARCH_OUTPUT_MAX)
    if not search_result['data']:
        return -1
    keyboard = []
    for i, company in enumerate(search_result['data']):
        keyboard.append([InlineKeyboardButton(f"{i + 1}. {company['instrument_name']}, {company['symbol']}, {company['exchange']}", 
                        callback_data=f'Found_companies:{company['instrument_name']}:{company['symbol']}:{company['exchange']}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def send_real_time_data(raw_data, update, context):
    await generate_stock_chart(raw_data)
    await send_image_local(update, context)

async def reset_user(user_tg_id):
    await delete_data('LinkTable', 'user_tg_id', user_tg_id)
    await update_user(user_tg_id, 'following', 0)
    await update_user(user_tg_id, 'status', 'Idle')