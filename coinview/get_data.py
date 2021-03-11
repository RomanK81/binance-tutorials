import config, csv
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

# prices = client.get_all_tickers()

# for price in prices:
#     print(price)

csvfile = open('2020_15minutes.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')

candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2020", "12 Jul, 2020")
#candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2020", "12 Jul, 2020")
#candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2017", "12 Jul, 2020")

for candlestick in  candlesticks:
    candlestick[0] = candlestick[0] / 1000
    candlestick_writer.writerow(candlestick)

csvfile.close()
"""
##################################################################################################
### Not historical data
## https://python-binance.readthedocs.io/en/latest/binance.html?highlight=get_klines#binance.client.Client.get_klines
candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_15MINUTE)

csvfile = open('data/15minutes_my2.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')
for candlestick in  candles:
    #candlestick[0] = candlestick[0] / 1000
    candlestick_writer.writerow(candlestick)

csvfile.close()
# # [
# #     [
# #         1499040000000,      # Open time
# #         "0.01634790",       # Open
# #         "0.80000000",       # High
# #         "0.01575800",       # Low
# #         "0.01577100",       # Close
# #         "148976.11427815",  # Volume
# #         1499644799999,      # Close time
# #         "2434.19055334",    # Quote asset volume
# #         308,                # Number of trades
# #         "1756.87402397",    # Taker buy base asset volume
# #         "28.46694368",      # Taker buy quote asset volume
# #         "17928899.62484339" # Can be ignored
# #     ]
# # ]

"""

