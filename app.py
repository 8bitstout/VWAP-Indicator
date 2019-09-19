import requests
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from datetime import time
from datetime import datetime

api_key = os.environ["ALPHAVANTAGE_API_KEY"]
stock_ticker = "aapl"
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=5min&apikey=%s' % (stock_ticker, api_key)

headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

response = requests.request('GET', url, headers=headers)
data = response.json()

meta_data = data["Meta Data"]
time_series = data["Time Series (5min)"]
trades = []
timestamps = []
volume_y = []
time_x = []
prices = []

def average_price(high, low, close):
  return (high + low + close) / 3

def date_is_current(timestamp):
  d = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
  return d.date() >= date.today()

def calculate_vwap(volumes, prices):
  vwap = []
  avg_pv = 0
  avg_v = 0
  for (index, volume) in enumerate(volumes):
    price = prices[index]
    pv = volume * price
    avg_pv += pv
    avg_v += volume
    vwap.append(avg_pv/avg_v)
  return vwap

for i in meta_data:
  print(meta_data[i])

for interval in time_series:
  if (date_is_current(interval)):
    high = float(time_series[interval]["2. high"])
    low = float(time_series[interval]["3. low"])
    close = float(time_series[interval]["4. close"])
    volume = int(time_series[interval]["5. volume"])
    average = average_price(high=high, low=low, close=close)
    trades.append({ "time": interval, "price": average, "volume": volume })
    volume_y.append(volume)
    time_x.append(datetime.strptime(interval, "%Y-%m-%d %H:%M:%S"))
    prices.append(average)
    timestamps.append(interval)

time_x.reverse()
volume_y.reverse()
prices.reverse()
vwap = calculate_vwap(volumes=volume_y, prices=prices)
print(vwap)

fig, ax1 = plt.subplots()
color = "tab:red"
ax1.set_xlabel("time")
ax1.set_ylabel("volume", color=color)
ax1.plot(time_x, volume_y, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()

color = "tab:blue"
ax2.set_ylabel("vwap", color=color)
ax2.plot(time_x, vwap, color=color)
ax2.tick_params(axis="y", labelcolor=color)

ax3 = ax1.twinx()
color = "tab:green"
ax3.plot(time_x, prices, color=color)

fig.tight_layout()
plt.title(stock_ticker)
plt.legend()
plt.show()
