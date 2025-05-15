import sqlite3
import config
import asyncio
from datetime import datetime

con = sqlite3.connect('bot_db.sqlite')
db_cursor = con.cursor()


async def add_data(table, *args):
    try:
        print(args)
        if table == 'Users':        #Добавление пользователя, требует id юзера в Telegram
            result = db_cursor.execute(f'INSERT INTO Users (user_tg_id, following, info_requests, ai_requests, status)' \
                                    f'VALUES ({args[0]}, {0}, {config.STOCKS_INFO_REQUESTS}, {config.AI_REQUESTS}, "None")').fetchone()
        elif table == 'Companies':  #Добавление новой компании, требует название компании, её тикер и рынок
            result = db_cursor.execute(f'INSERT INTO Companies (company_name, company_ticker, exchange)' \
                                   f'VALUES ("{args[0]}", "{args[1]}", "{args[2]}")').fetchone()
        elif table == 'Shares':     #Добавление информации о цене акций, требует ticker символ компании, дату и время, стоимость акции
            result = db_cursor.execute(f'INSERT INTO Shares (company_id, datetime, price)' \
                                   f'VALUES ("{args[0]}", "{args[1]}", "{args[2]}")').fetchone()
        elif table == 'LinkTable':  #Добавление связки между пользователем и компанией, которую он отслеживает, требует id компании и id пользователя
            result = db_cursor.execute(f'INSERT INTO LinkTable (user_tg_id, company_id)' \
                                       f'VALUES ("{args[0]}", "{args[1]}")').fetchone()
        con.commit()
        return result
    except sqlite3.IntegrityError as e:
        return e

async def get_data(table, what, criteria, x):
    result = db_cursor.execute(f'SELECT {what} FROM {table} WHERE {criteria} = {x}').fetchone()
    if result == None:
        return Exception(f'{x} was not found by {criteria} in {table}')
    else:
        result = result
    return result

async def delete_data(table, criteria, x):
    result = db_cursor.execute(f'DELETE FROM {table} WHERE {criteria} = "{x}"')
    con.commit()
    return result

async def update_user(user_tg_id, param, new_value):
    result = db_cursor.execute(f'UPDATE Users SET "{param}" = "{new_value}" WHERE user_tg_id = "{user_tg_id}"')
    con.commit()
    return result

async def get_companies_list():
    result = db_cursor.execute(f'SELECT company_ticker, exchange FROM Companies').fetchall()
    return result

async def check_subscription(user_tg_id, symbol, exchange):
    company_id = await get_company_id(symbol, exchange)
    result = db_cursor.execute(f'SELECT * FROM LinkTable WHERE user_tg_id = "{user_tg_id}" AND company_id = "{company_id}"').fetchone()
    print(result, company_id)
    if not result:
        return False
    return True

async def get_company_id(symbol, exchange):
    result = db_cursor.execute(f'SELECT company_id FROM Companies WHERE company_ticker = "{symbol}" AND ' \
                               f'exchange = "{exchange}"').fetchone()
    return result[0]

async def main_f():
    await check_subscription('5100407614', 'SPOT', 'NYSE')
