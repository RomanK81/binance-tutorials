from binance.enums import *
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
import math 
import json
import config

class ClientBinance():

    def __init__(self, logger):
        self.logger = logger
        self.client = Client(config.API_KEY, config.API_SECRET)#, tld='us'
        self.bf_client  = RequestClient(api_key=config.API_KEY, secret_key=config.API_SECRET, url="https://fapi.binance.com")

    def get_data(self):
        #global worker_kline_thr
        account = self.client.get_account()

        balances = account['balances']
        # if not worker_thread.isAlive():
        #     print("Starting kline Thread")
        #     worker_kline_thr.start()


        exchange_info = self.client.get_exchange_info()

        symbols = exchange_info['symbols']
        btcusdt_idx = next(i for i, elem in enumerate(symbols) if elem['symbol'] =='BTCUSDT')
        symbols.insert(0, symbols.pop(btcusdt_idx))

        return balances, symbols

    def create_order(self, **data):
        symbol = data['symbol']
        side = data['side']
        order_type = data['order_type']
        quantity = data['quantity']

        if 'price' in data:
            price = float(data['price'])
        else:
            current_price = self.client.get_symbol_ticker(symbol=symbol)
            self.logger.info(current_price)
            price = float(current_price['price'])

        if('percentage' in data and data['percentage'] > 0):
            percentage = data['percentage']
            if symbol.endswith('USDT'):
                asset = symbol[:-4]
                base = 'USDT'
            else: # BTC or BNB
                asset = symbol[:-3]
                base = symbol[-3:]

            asset_balance = self.client.get_asset_balance(asset=asset) 
            base_balance = self.client.get_asset_balance(asset=base) 

            self.logger.info(asset_balance)
            self.logger.info(base_balance)


            if side == 'BUY':
                quantity = float(base_balance['free']) *  float(percentage)/float(price)*0.9995
            else:
                quantity = float(asset_balance['free']) * float(percentage)*0.9995

        filters = self.client.get_symbol_info(symbol)['filters']
        tick_size = float(list(filter(lambda dum: dum['filterType'] == 'PRICE_FILTER', filters))[0]['tickSize'])
        step_size = float(list(filter(lambda dum: dum['filterType'] == 'LOT_SIZE', filters))[0]['stepSize'])

        quantity = float(ClientBinance.float_precision(quantity, step_size))

        try:
            if config.TEST:
                self.logger.info('Test order!')
                return self._make_order(symbol, side, order_type, quantity, price, tick_size, self.client.create_test_order)

            return self._make_order(symbol, side, order_type, quantity, price, tick_size, self.client.create_order)

        except BinanceAPIException as e:
            return e.message
        except BinanceOrderException as e:
            return e.message

    #self.client.create_test_order
    def _make_order(self, symbol, side, order_type, quantity, price, tick_size, create_order):

        self.logger.info(f'Order: {side} by {order_type}, symbol: {symbol}, price: {price}, quantity: {quantity}, cost: {float(price)*quantity}')

        if order_type == 'MARKET':
            return create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)

        if 'LIMIT' in order_type:

            price = ClientBinance.float_precision(price, tick_size)

            if 'STOP' in order_type:
                if side=='BUY':
                    stopPrice = ClientBinance.float_precision( float(price)*0.9999, tick_size) #real = 0.95, test = 0.9999
                else:
                    stopPrice = ClientBinance.float_precision( float(price)*1.0001, tick_size) #real = 1.25, test = 1.0001

                return create_order(symbol=symbol, side=side, type='STOP_LOSS_LIMIT', timeInForce='GTC',
                                            stopPrice = stopPrice, price=price, quantity=quantity)

            return create_order(symbol=symbol, side=side, type='LIMIT', timeInForce='GTC',
                                                price=price , quantity=quantity)

        if 'PUMP' in order_type:
            res = create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity)
            self.logger.info('PUMP: BUY result: ', res)

            price = ClientBinance.float_precision(price, tick_size)

            stop_price = float(price)*0.9999 # Not test *0.95
            current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            target_price = float(price)*1.0001 # Not test *1.25

            while current_price < target_price and current_price >= stop_price:
                current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
                self.logger.debug('stop', stop_price, 'price', current_price, 'target', target_price)

                if current_price>=target_price:
                    stop_price = target_price
                    target_price = target_price * 1.25 # Not test *1.05

            res = create_order(symbol=symbol, side='SELL', type='MARKET', quantity=quantity)
            if current_price >= target_price:
                self.logger.info('take profit at', current_price,'percentage', round( (current_price/float(price)-1)*100, 2) )
            else:
                self.logger.info('stop loss at', current_price, 'percentage', round( (current_price/float(price)-1) *100, 2) )
            return res

    @staticmethod
    def float_precision(f, n):
        n = int(math.log10(1 / float(n)))
        f = math.floor(float(f) * 10 ** n) / 10 ** n
        f = "{:0.0{}f}".format(float(f), n)
        return str(int(f)) if int(n) == 0 else f

    def get_historical_data(self):
        #data_end = f"{datetime.datetime.utcnow():%d %B, %Y}"
        #start_ts = f"{(datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(months=1)):%d %B, %Y}"
        #candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, start_str=start_ts, end_str=data_end)
        candlesticks = self.client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 month ago UTC")

        processed_candlesticks = []

        for data in candlesticks:
            processed_candlesticks.append({
                "time": data[0] / 1000,
                "open": data[1],
                "high": data[2],
                "low": data[3],
                "close": data[4]
            })

        oi = [*self.bf_client.get_open_interest_stats(symbol="BTCUSDT", period='2h',limit=500)]

        # oiticks = []
        # for i in oi:
        #     oiticks.append({
        #         "time": int(i.timestamp[:-3]),
        #         "value": i.sumOpenInterestValue,
        #     })
        oi_data = self._get_ai_data(oi)

        return processed_candlesticks, oi_data

    def get_open_interest(self):
        #global  bf_client
        #time.sleep(sleep)
        #binf_client  = RequestClient(api_key=config.API_KEY, secret_key=config.API_SECRET, url="https://fapi.binance.com")
        oi = [*self.bf_client.get_open_interest_stats(symbol="BTCUSDT", period='15m', limit=1)]

        data =self._get_ai_data(oi)

        my_dict = {}
        my_dict["data"]={}
        my_dict["data"]["e"]='oi'
        my_dict["data"]["oiticks"] = data

        return json.dumps(my_dict)

    def _get_ai_data(self, oi):
        oiticks = []
        for i in oi:
            oiticks.append({
                "time": int(i.timestamp[:-3]),
                "value": i.sumOpenInterest,
            })
        return oiticks
