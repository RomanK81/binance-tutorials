from flask import Flask, render_template, request, flash, redirect, jsonify
from flask_cors import CORS, cross_origin
import csv, datetime
import config
import dateutil.relativedelta
from binance.enums import *
from binance.client import Client
from binance.enums import *

app = Flask(__name__)
app.secret_key = b'sadasf879f8asuih!qwee2ee23##9&$'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = Client(config.API_KEY, config.API_SECRET)#, tld='us'

allow_origin_list = ['http://localhost:5000']


@app.route('/')
@cross_origin()
def index():
    title = 'CoinView'

    account = client.get_account()

    balances = account['balances']

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=balances[:5], symbols=symbols)


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
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    response = jsonify(processed_candlesticks)
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5000')
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN']  in allow_origin_list:
        response.headers.add('Access-Control-Allow-Origin', request.environ['HTTP_ORIGIN'] )
    return response