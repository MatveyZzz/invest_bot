from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import asyncio

import config
from finance_info import company_search

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