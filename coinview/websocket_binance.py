import threading
import time
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from threading import Thread, Event

class WebSocetBinance():

    def __init__(self, socketio, logger) -> None:
        self.binance_websocket = BinanceWebSocketApiManager(exchange="binance.com")
        self.logger = logger
        self.socketio = socketio
        markets =['btcusdt']
        # channels = ['kline_1m', 'kline_5m', 'kline_15m', 'kline_30m', 'kline_1h', 'kline_12h', 'kline_1w', 'trade',
        #             'miniTicker','ticker', 'depth20']
        channels = ['kline_15m']

        for channel in channels:
            self.binance_websocket.create_stream(channel, markets)

        self.worker_thread = Thread(target=self._print_stream_data_from_stream_buffer)

    def connect(self):
        if not self.worker_thread.isAlive():
            self.logger.info("Websocet thread started")
            self.worker_thread.start()

    #@staticmethod
    def _print_stream_data_from_stream_buffer(self):
        time.sleep(5)
        #threading.Timer(900, _get_open_interest).start()
        while True:
            if self.binance_websocket.is_manager_stopping():
                exit(0)
            stream = self.binance_websocket.pop_stream_data_from_stream_buffer()
            if stream is False:
                time.sleep(0.01)
            else:
                try:
                    # remove # to activate the print function:
                    # print(stream)
                    self.socketio.emit('stream', stream, namespace='/binance')
                except KeyError:
                    # Any kind of error...
                    # not able to process the data? write it back to the stream_buffer
                    self.binance_websocket.add_to_stream_buffer(stream)

#SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_15m"
# def k_line_func(ws):
#     ws.run_forever()

# def on_open(ws):
#     print('opened connection')

# def on_close(ws):
#     print('closed connection')

# def on_message(ws, message):
#     json_message = json.loads(message)
#     pprint.pprint(json_message)

#ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
#worker_kline_thr = Thread(target=k_line_func, args=(ws,))