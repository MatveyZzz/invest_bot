
import matplotlib.pyplot as plt
from datetime import datetime

async def generate_stock_chart(data):
    # Извлечение данных
    symbol = data['meta']['symbol']
    #company_name = data['meta']['instrument_name']
    exchange = data['meta']['exchange']
    currency = data['meta']['currency']
    values = data['values']

    # Обработка данных
    dates = [datetime.strptime(val['datetime'], "%Y-%m-%d %H:%M:%S") for val in values]
    closes = [float(val['close']) for val in values]

    # Определение цвета линии
    color = "green" if closes[-1] >= closes[0] else "red"

    # Построение графика
    plt.figure(figsize=(10, 7))
    plt.plot(dates, closes, color=color, linewidth=2, marker="o")
    #plt.title(f"{company_name} ({symbol}) — {exchange}", fontsize=14)
    plt.xlabel("Дата", fontsize=12)
    plt.ylabel(f"Цена закрытия ({currency})", fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохранение изображения
    plt.savefig("stock_chart.png")
    plt.close()
