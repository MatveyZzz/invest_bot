import sqlite3
import config

con = sqlite3.connect('bot_db.sqlite')
db_cursor = con.cursor()

def add_user_data(user_tg_id):
    try:
        result = db_cursor.execute(f"INSERT INTO Users (user_tg_id, following, info_requests, ai_requests)" \
                                   f"VALUES ({user_tg_id}, {0}, {config.STOCKS_INFO_REQUESTS}, {config.AI_REQUESTS})").fetchone()
        con.commit()
        print(result)
    except sqlite3.IntegrityError as e:
        return e

def delete_user_data(user_tg_id):
    result = db_cursor.execute(f'DELETE FROM Users WHERE user_tg_id = "{user_tg_id}"')
    con.commit()
    return result


def get_user_data(user_tg_id):
    result = db_cursor.execute(f'SELECT * FROM Users WHERE user_id = {user_tg_id}').fetchone()
    if result == None:
        return Exception("User was not found")
    return result
