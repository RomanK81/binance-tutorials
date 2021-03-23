// https://www.cssscript.com/financial-chart/

// https://www.tradingview.com/lightweight-charts/
// https://jsfiddle.net/TradingView/gemn0ud6/
// https://jsfiddle.net/BlackLabel/zrd3meyq/1/

// https://www.amcharts.com/demos/live-order-book-depth-chart/
// https://data.bitcoinity.org/markets/price_volume/all/USD?r=week&t=lb
var chart = LightweightCharts.createChart(document.getElementById('chart'), {
	width: 1500,
  	height: 500,
	rightPriceScale: {
		visible: true,
    	borderColor: 'rgba(197, 203, 206, 1)',
	},
	leftPriceScale: {
		visible: true,
    	borderColor: 'rgba(197, 203, 206, 1)',
	},
	layout: {
		backgroundColor: '#000000',
		textColor: 'rgba(255, 255, 255, 0.9)',
	},
	grid: {
		vertLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
		horzLines: {
			color: 'rgba(197, 203, 206, 0.5)',
		},
	},
	crosshair: {
		mode: LightweightCharts.CrosshairMode.Normal,
	},
	timeScale: {
		borderColor: 'rgba(197, 203, 206, 0.8)',
		timeVisible: true,
		secondsVisible: false,
	},
	handleScroll: {
		vertTouchDrag: false,
	},
});

var candleSeries = chart.addCandlestickSeries({
	upColor: '#00ff00',
	downColor: '#ff0000', 
	borderDownColor: 'rgba(255, 144, 0, 1)',
	borderUpColor: 'rgba(255, 144, 0, 1)',
	wickDownColor: 'rgba(255, 144, 0, 1)',
	wickUpColor: 'rgba(255, 144, 0, 1)',
});

var lineSeries = chart.addLineSeries({
	color: 'rgba(4, 111, 232, 1)',
	lineWidth: 2,
	priceScaleId: 'left'
});

fetch('http://' + document.domain + ':' + location.port + '/history',{ mode: 'cors'})
	.then((r) => r.json())
	.then((response) => {
		console.log(response)

		candleSeries.setData(response['candlesticks']);

		lineSeries.setData(response['oiticks']);

		chart.timeScale().fitContent();
	})
	.catch((error) => {
		console.log(error)
		//reject(error)
	})

var socket = io.connect('http://' + document.domain + ':' + location.port + '/binance');

//receive details from server
socket.on('stream', function (event) {
	var message = JSON.parse(event);

	if(!message.data)
		return;

	if(message.data.e == 'kline'){
		var candlestick = message.data.k;

		candleSeries.update({
			time: candlestick.t / 1000,
			open: candlestick.o,
			high: candlestick.h,
			low: candlestick.l,
			close: candlestick.c
		})
	}
	if(message.data.e == 'oi'){
		message.data.oiticks.forEach(element => {
			lineSeries.update({
				time: element.time,
				value: element.value
			})
		});
	}

})

// var binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@kline_15m");

// binanceSocket.onmessage = function (event) {	
// 	var message = JSON.parse(event.data);

// 	var candlestick = message.k;

// 	console.log(candlestick)

// 	candleSeries.update({
// 		time: candlestick.t / 1000,
// 		open: candlestick.o,
// 		high: candlestick.h,
// 		low: candlestick.l,
// 		close: candlestick.c
// 	})
// }
//