import sqlite3
import config

con = sqlite3.connect('bot_db.sqlite')
db_cursor = con.cursor()


def add_user(user_tg_id):
    try:
        result = db_cursor.execute(f'INSERT INTO Users (user_tg_id, following, info_requests, ai_requests)' \
                                   f'VALUES ({user_tg_id}, {0}, {config.STOCKS_INFO_REQUESTS}, {config.AI_REQUESTS})').fetchone()
        con.commit()
        print(result)
    except sqlite3.IntegrityError as e:
        return e

def delete_user(user_tg_id):
    result = db_cursor.execute(f'DELETE FROM Users WHERE user_tg_id = "{user_tg_id}"')
    con.commit()
    return result

def update_user(user_tg_id, param, new_value):
    result = db_cursor.execute(f'UPDATE Users SET {param} = {new_value} WHERE user_tg_id = "{user_tg_id}"')
    con.commit()
    return result

def get_user_data(user_tg_id):
    result = db_cursor.execute(f'SELECT * FROM Users WHERE user_tg_id = {user_tg_id}').fetchone()
    if result == None:
        return Exception('User was not found')
    return f"ID: {result[0]}\nTG_ID: {result[1]}\nFOLLOWING: {result[2]}\nINFO_REQS: {result[3]}\nAI_REQS: {result[4]}"

def add_company(company_name, company_ticker):
    try:
        result = db_cursor.execute(f'INSERT INTO Companies (company_name, company_ticker)' \
                                   f'VALUES ("{company_name}", "{company_ticker}")').fetchone()
        con.commit()
        print(result)
    except sqlite3.IntegrityError as e:
        return e

def delete_company(company_name):
    result = db_cursor.execute(f'DELETE FROM Companies WHERE company_name = "{company_name}"')
    con.commit()
    return result

def get_company_data(company_name):
    result = db_cursor.execute(f'SELECT * FROM Companies WHERE company_name = "{company_name}"').fetchone()
    if result == None:
        return Exception('Company was not found')
    return f"ID: {result[0]}\nNAME: {result[1]}\nTICKER: {result[2]}"

delete_company("Apple Inc.")