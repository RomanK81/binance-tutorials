from __future__ import print_function
from flask import Flask, render_template, request, flash, redirect, jsonify
from flask_cors import CORS, cross_origin
from flask_socketio  import SocketIO
#import websocket, json, pprint
import csv, datetime
import config
import dateutil.relativedelta
from binance.enums import *
from binance.client import Client
from binance.enums import *
import time, threading

from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import logging
import time
from threading import Thread, Event
import os

from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *

app = Flask(__name__)
app.secret_key = b'sadasf879f8asuih!qwee2ee23##9&$'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, async_mode=None)
client = Client(config.API_KEY, config.API_SECRET)#, tld='us'

bf_client  = RequestClient(api_key=config.API_KEY, secret_key=config.API_SECRET, url="https://fapi.binance.com")

binance_websocket = BinanceWebSocketApiManager(exchange="binance.com")

allow_origin_list = ['http://localhost:5000']

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")


markets =['btcusdt']
# channels = ['kline_1m', 'kline_5m', 'kline_15m', 'kline_30m', 'kline_1h', 'kline_12h', 'kline_1w', 'trade',
#             'miniTicker','ticker', 'depth20']
channels = ['kline_15m']

for channel in channels:
    binance_websocket.create_stream(channel, markets)

def print_stream_data_from_stream_buffer(binance_websocket):
    print("waiting 5 seconds, then we start flushing the stream_buffer")
    time.sleep(5)
    _get_open_interest(10)
    while True:
        if binance_websocket.is_manager_stopping():
            exit(0)
        stream = binance_websocket.pop_stream_data_from_stream_buffer()
        if stream is False:
            time.sleep(0.01)
        else:
            try:
                # remove # to activate the print function:
                # print(stream)
                socketio.emit('stream', stream, namespace='/binance')
            except KeyError:
                # Any kind of error...
                # not able to process the data? write it back to the stream_buffer
                binance_websocket.add_to_stream_buffer(stream)

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

worker_thread = Thread(target=print_stream_data_from_stream_buffer, args=(binance_websocket,))

@app.route('/')
@cross_origin()
def index():
    title = 'CoinView'
    #global worker_kline_thr
    account = client.get_account()

    balances = account['balances']
    # if not worker_thread.isAlive():
    #     print("Starting kline Thread")
    #     worker_kline_thr.start()

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=balances[:5], symbols=symbols)

@socketio.on('connect', namespace='/binance')
def binance_connect():
    # need visibility of the global thread object
    global worker_thread
    print('Client connected')

    if not worker_thread.isAlive():
        print("Starting Thread")
        worker_thread.start()


@app.route('/buy', methods=['POST'])
@cross_origin()
def buy():
    print(request.form)
    try:
        order = client.create_order(
            symbol = request.form['symbol'], 
            side = SIDE_BUY,
            type = ORDER_TYPE_MARKET,
            quantity = request.form['quantity'])
    except Exception as e:
        flash(e.message, "error")

    return redirect('/')


@app.route('/sell')
def sell():
    return 'sell'


@app.route('/settings')
def settings():
    return 'settings'

@app.route('/history')
#@cross_origin()
def history():
    #data_end = f"{datetime.datetime.utcnow():%d %B, %Y}"
    #start_ts = f"{(datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(months=1)):%d %B, %Y}"
    #candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, start_str=start_ts, end_str=data_end)
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 month ago UTC")

    processed_candlesticks = []

    for data in candlesticks:
        processed_candlesticks.append({
            "time": data[0] / 1000,
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4]
        })

    oi = [*bf_client.get_open_interest_stats(symbol="BTCUSDT", period='1h',limit=500)]

    # oiticks = []
    # for i in oi:
    #     oiticks.append({
    #         "time": int(i.timestamp[:-3]),
    #         "value": i.sumOpenInterestValue,
    #     })

    response = jsonify({
        "candlesticks":processed_candlesticks,
        "oiticks": _get_ai_data(oi)
    })
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5000')
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN']  in allow_origin_list:
        response.headers.add('Access-Control-Allow-Origin', request.environ['HTTP_ORIGIN'] )
    return response

def _get_open_interest(sleep=0):
    global  bf_client
    time.sleep(sleep)
    oi = [*bf_client.get_open_interest_stats(symbol="BTCUSDT", period='1m')]

    data =_get_ai_data(oi)

    stream = jsonify({
        "data":{
            "e":"oi",
            "oiticks": data
        }
    })

    socketio.emit('stream', stream, namespace='/binance')
    threading.Timer(100, _get_open_interest).start()

def _get_ai_data(oi):
    oiticks = []
    for i in oi:
        oiticks.append({
            "time": int(i.timestamp[:-3]),
            "value": i.sumOpenInterestValue,
        })
    return oiticks

if __name__ == '__main__':
    socketio.run(app)