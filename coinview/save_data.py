import config, csv

from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *

bf_client  = RequestClient(api_key=config.API_KEY, secret_key=config.API_SECRET, url="https://fapi.binance.com")


'''
If startTime and endTime are not sent, the most recent data is returned. (startTime='1609452000', endTime='1610229600', )
Only the data of the latest 30 days is available.
'''
result = bf_client.get_open_interest_stats(symbol="BTCUSDT", period='1h',limit=500)
'''
print("======= Get Open Interest Stats =======")
PrintMix.print_data(result)
print("==========================================")
data number 378 :
json_parse:<function OpenInterestStats.json_parse at 0x000001C6056A5378>
sumOpenInterest:30904.696
sumOpenInterestValue:1569483926.334811
symbol:BTCUSDT
timestamp:1615215600000


data number 379 :
json_parse:<function OpenInterestStats.json_parse at 0x000001C6056A5378>
sumOpenInterest:31136.003
sumOpenInterestValue:1590188824.3291142
symbol:BTCUSDT
timestamp:1615219200000
'''

csvfile = open('data/foi_1h_1y.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')
for oi in  result:
    oi.timestamp = str(int(int(oi.timestamp)/ 1000))
    candlestick_writer.writerow([oi.timestamp,oi.sumOpenInterest, oi.sumOpenInterestValue])

csvfile.close()
"""
[
    { 
         "symbol":"BTCUSDT",
          "sumOpenInterest":"20403.63700000",  // total open interest 
          "sumOpenInterestValue": "150570784.07809979",   // total open interest value
          "timestamp":"1583127900000"

     },

     {

         "symbol":"BTCUSDT",
         "sumOpenInterest":"20401.36700000",
         "sumOpenInterestValue":"149940752.14464448",
         "timestamp":"1583128200000"

        },   

]
"""

