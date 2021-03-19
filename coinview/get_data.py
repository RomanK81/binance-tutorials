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

https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
# Kline/Candlestick Streams
{
  "e": "kline",     // Event type
  "E": 123456789,   // Event time
  "s": "BNBBTC",    // Symbol
  "k": {
    "t": 123400000, // Kline start time
    "T": 123460000, // Kline close time
    "s": "BNBBTC",  // Symbol
    "i": "1m",      // Interval
    "f": 100,       // First trade ID
    "L": 200,       // Last trade ID
    "o": "0.0010",  // Open price
    "c": "0.0020",  // Close price
    "h": "0.0025",  // High price
    "l": "0.0015",  // Low price
    "v": "1000",    // Base asset volume
    "n": 100,       // Number of trades
    "x": false,     // Is this kline closed?
    "q": "1.0000",  // Quote asset volume
    "V": "500",     // Taker buy base asset volume
    "Q": "0.500",   // Taker buy quote asset volume
    "B": "123456"   // Ignore
  }
}

"""

