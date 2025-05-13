from data_manage import add_data, get_data, delete_data
from data_manage import update_company_data, update_user
from dotenv import load_dotenv
import json
import requests
import os
import config

load_dotenv()

request_template = 'https://api.twelvedata.com/'

def get_time_series(company_symbol):
    request_url = request_template + f'time_series?symbol={company_symbol}&interval={config.FIN_DATA_INTERVAL}&type=Common Stock' \
        f'&outputsize={config.FIN_DATA_OUTPUTS}&apikey={os.getenv("TWELVE_API_KEY")}'
    response = requests.get(request_url)
    if response:
        json_data = response.json()
        for row in range(config.FIN_DATA_OUTPUTS):
            add_data('Shares', json_data['meta']['symbol'], json_data['values'][row]['datetime'], json_data['meta']['currency'], 
                 json_data['values'][row]['open'], json_data['values'][row]['close'], json_data['values'][row]['high'], json_data['values'][row]['low'])

def company_search(entered_symbol):
    request_url = request_template + f'symbol_search?symbol={entered_symbol}'
    response = requests.get(request_url)
    if response:
        json_data = response.json()
        print(json_data)
        return json_data['data']

def get_real_time_cost(company_symbol):
    request_url = request_template + f'price?symbol={company_symbol}&type=Common Stock&apikey={os.getenv("TWELVE_API_KEY")}'
    response = requests.get(request_url)
    if response:
        json_data = response.json()
        print(json_data)

def convert_currency():
    pass

if __name__ == '__main__':
    company_search("AAPL")
