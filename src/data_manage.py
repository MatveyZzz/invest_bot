import sqlite3
import config

con = sqlite3.connect('bot_db.sqlite')
db_cursor = con.cursor()

### Попробовать упростить
def add_data(table, *args):
    try:
        print(args)
        if table == 'Users':        #Добавление пользователя, требует id юзера в Telegram
            result = db_cursor.execute(f'INSERT INTO Users (user_tg_id, following, info_requests, ai_requests)' \
                                    f'VALUES ({args[0]}, {0}, {config.STOCKS_INFO_REQUESTS}, {config.AI_REQUESTS})').fetchone()
        elif table == 'Companies':  #Добавление новой компании, требует название компании, её тикер и полную стоимость компании
            result = db_cursor.execute(f'INSERT INTO Companies (company_name, company_ticker, company_cost)' \
                                   f'VALUES ("{args[0]}", "{args[1]}", "{args[2]}")').fetchone()
        elif table == 'Shares':     #Добавление информации о цене акций, требует id компании, дату, время, стоимость акции
            result = db_cursor.execute(f'INSERT INTO Shares (company_symbol, date_time, currency, open, close, high, low)' \
                                   f'VALUES ("{args[0]}", "{args[1]}", "{args[2]}", {args[3]}, {args[4]}, {args[5]}, {args[6]})').fetchone()
        elif table == 'LinkTable':  #Добавление связки между пользователем и компанией, которую он отслеживает, требует id компании и id пользователя
            result = db_cursor.execute(f'INSERT INTO LinkTable (user_id, company_id)' \
                                       f'VALUES ({args[0]}, {args[1]})').fetchone()
        con.commit()
        print(result)
    except sqlite3.IntegrityError as e:
        return e

def get_data(table, criteria, x):
    result = db_cursor.execute(f'SELECT * FROM {table} WHERE {criteria} = {x}').fetchone()
    if result == None:
        return Exception(f'{x} was not found by {criteria} in {table}')
    else:
        result = (table, *result)
    return result

def delete_data(table, criteria, x):
    result = db_cursor.execute(f'DELETE FROM {table} WHERE {criteria} = "{x}"')
    con.commit()
    return result

def update_user(user_tg_id, param, new_value):
    result = db_cursor.execute(f'UPDATE Users SET {param} = {new_value} WHERE user_tg_id = "{user_tg_id}"')
    con.commit()
    return result

if __name__ == '__main__':
    print(get_data('Users', 'user_tg_id', '12352'))
    