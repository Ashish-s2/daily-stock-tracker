# stock_tracker.py

import yfinance as yf
import datetime
import os
import pandas as pd

# Stock symbol for Dixon Tech (NSE)
symbols = ['DIXON.NS']

# Get today's date
today = datetime.datetime.now().strftime('%Y-%m-%d')
folder = 'stocks'
os.makedirs(folder, exist_ok=True)
filename = f"{folder}/{today}.csv"

# Download data
data = []
for symbol in symbols:
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")
    if not price.empty:
        current_price = price['Close'].iloc[-1]
        data.append([today, symbol, round(current_price, 2)])

# Save to CSV
df = pd.DataFrame(data, columns=["Date", "Symbol", "Price"])
df.to_csv(filename, index=False)
