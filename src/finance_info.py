from dotenv import load_dotenv
import os
from datetime import datetime

from aiohttp import ClientSession
import asyncio

from data_manage import get_companies_list, get_company_id, add_data

load_dotenv()

request_template = 'https://api.twelvedata.com/'


async def get_real_time_price(company_symbol, exchange):
    async with ClientSession() as session:
        url = 'https://api.twelvedata.com/price'
        params = {'symbol': company_symbol, 'exchange': exchange, 'type': 'Common Stock', 'apikey': os.getenv("TWELVE_API_KEY")}
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            result['company_id'] = (await get_company_id(company_symbol, exchange))[0]
            result['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return result

async def get_time_series(company_symbol, exchange, interval, outputsize):
    url = 'https://api.twelvedata.com/time_series'
    params = {'symbol': company_symbol, 'exchange': exchange, 'interval': interval, 'type': 'Common Stock', 
                'outputsize': outputsize, 'apikey': os.getenv("TWELVE_API_KEY")}
    async with ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            return result

async def company_search(entered_symbol, outputsize):
    url = 'https://api.twelvedata.com/symbol_search'
    params = {'symbol': entered_symbol, 'outputsize': outputsize}
    async with ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            return result

async def update_companies_real_time_cost():
    tasks = []
    companies = await get_companies_list()
    for company in companies:
        tasks.append(asyncio.create_task(get_real_time_price(company[0], company[1])))
    results = await asyncio.gather(*tasks)
    print(results)
    tasks = []
    for result in results:
        tasks.append(asyncio.create_task(add_data('Shares', result['company_id'], result['datetime'], result['price'])))  


async def main_func():
    result = await company_search('BRUH', 5)
    print(result)

if __name__ == '__main__':
    asyncio.run(main_func())
