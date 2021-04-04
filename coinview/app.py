from __future__ import print_function
from flask import Flask, json, render_template, request, flash, redirect, jsonify, make_response
from flask_cors import CORS, cross_origin
from flask_socketio  import SocketIO
from waitress import serve
#import websocket, json, pprint
import config
import threading
import logging
import os

from client_binance import ClientBinance
from websocket_binance import WebSocetBinance

app = Flask(__name__)# static_url_path='', static_folder=''
app.secret_key = config.SECRET
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, async_mode=None)#, async_mode='threading'

allow_origin_list = [f'http://localhost:{config.PORT}']

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
#unicorn_binance_websocket_api_socket

logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

client = ClientBinance(logging)

binance_websocket = WebSocetBinance(socketio, logging)
logging.getLogger('BinanceWebSocketApiManager').setLevel(logging.ERROR)

@app.route('/')
@cross_origin()
def index():
    title = 'CoinView'

    threading.Timer(900, _get_open_interest).start()

    balances, symbols = client.get_data()
    return render_template('index.html', title=title, my_balances=balances[:5], symbols=symbols)

@socketio.on('connect', namespace='/binance')
def connect():
    binance_websocket.connect()

'''
https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
Find : New order
https://academy.binance.com/en/articles/what-is-a-limit-order
'''
@app.route('/order', methods=['POST'])
@cross_origin()
def order():
    form_dict = request.form.to_dict()#flat=False
    logging.info(f'Order: {form_dict}')
    data = client.create_order(**form_dict)
    logging.info(f'Result Order: {data}')

    return make_response(jsonify(data.toJson()), 200)

    # if(isinstance(res, str)):
    #     flash(res, "error")
    # else:
    #     flash("Success", 'info')

    #return redirect('/')

@app.route('/history')
#@cross_origin()
def history():

    processed_candlesticks, oi_data = client.get_historical_data()

    response = jsonify({
        "candlesticks":processed_candlesticks,
        "oiticks": oi_data
    })
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5000')
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN']  in allow_origin_list:
        response.headers.add('Access-Control-Allow-Origin', request.environ['HTTP_ORIGIN'] )
    return response

def _get_open_interest(sleep=900):
    stream = client.get_open_interest()
    socketio.emit('stream', stream, namespace='/binance')
    threading.Timer(sleep, _get_open_interest).start()

if __name__ == '__main__':
    # from gevent import monkey
    # monkey.patch_all()
    socketio.run(app, host=config.HOST, port=config.PORT, debug=config.DEBUG)