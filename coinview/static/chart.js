// https://www.cssscript.com/financial-chart/

// https://www.tradingview.com/lightweight-charts/
// https://jsfiddle.net/TradingView/gemn0ud6/
// https://jsfiddle.net/BlackLabel/zrd3meyq/1/

// https://www.amcharts.com/demos/live-order-book-depth-chart/
// https://data.bitcoinity.org/markets/price_volume/all/USD?r=week&t=lb
// var container = document.createElement('chart');
// document.body.appendChild(container);

var container = document.getElementById('chart')
var chart = LightweightCharts.createChart(container, {
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

function businessDayToString(UNIX_timestamp) {
	var a = new Date(UNIX_timestamp * 1000);
	var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	var year = a.getFullYear();
	var month = months[a.getMonth()];
	var date = a.getDate();
	var hour = a.getHours();
	var min = a.getMinutes();
	var sec = a.getSeconds();
	var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
	return time;
}

var toolTipWidth = 80;
var toolTipHeight = 80;
var toolTipMargin = 15;

var toolTip = document.createElement('div');
toolTip.className = 'floating-tooltip-2';
container.appendChild(toolTip);

// update tooltip
chart.subscribeCrosshairMove(function(param) {
		if (param.point === undefined || !param.time || param.point.x < 0 || param.point.x > container.clientWidth || param.point.y < 0 || param.point.y > container.clientHeight) {
			toolTip.style.display = 'none';
		} else {
			const dateStr = businessDayToString(param.time);
			toolTip.style.display = 'block';
			var price = param.seriesPrices.get(lineSeries);
			var priceK = param.seriesPrices.get(candleSeries);

			toolTip.innerHTML = 
			'<div style="color: #009688">'+
				'Binance Kl/OI</div>'+
			'<div style="font-size: 24px; margin: 4px 0px; color: #21384d">'+
			 	Math.round(100 * price) / 100 +
			 '</div>'+
			 '<div style="font-size: 24px; margin: 4px 0px; color: #21384d">'+
			 	Math.round(100 * priceK.close) / 100 +
		 	'</div>'+
			 '<div style="color: #21384d">' +
			  	dateStr +
			 '</div>';

			var coordinate = lineSeries.priceToCoordinate(price);
			var shiftedCoordinate = param.point.x - 50;
			if (coordinate === null) {
				return;
			}
			shiftedCoordinate = Math.max(0, Math.min(container.clientWidth - toolTipWidth, shiftedCoordinate));
			var coordinateY = coordinate - toolTipHeight - toolTipMargin > 0 ? coordinate - toolTipHeight - toolTipMargin : Math.max(0, Math.min(container.clientHeight - toolTipHeight - toolTipMargin, coordinate + toolTipMargin));
			toolTip.style.left = shiftedCoordinate + 'px';
			toolTip.style.top = coordinateY + 'px';
		}
});

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

$(function() {
	// set up form validation here
	$("form").validate();
 });

 var markers = [];

 $("form").on("submit", function (e) {
    var dataString = $(this).serialize();

    $.ajax({
      type: "POST",
      url: "/order",
      data: dataString,
	  dataType:"json",
      success: function (data) {
		var $response=$.parseJSON(data);

		if(!$response.success){
			markers.push({
				time: new Date().getTime(),
				position: 'aboveBar',
				color: 'red',
				shape: 'circle',
				text: `${$response.data}`,
				size: 2,
			})
		}else{
			var order = $response.data;
			markers.push({
				time: order.transactTime,
				position: order.side == 'SELL' ? 'aboveBar' : 'belowBar',
				color: order.side == 'SELL' ? 'green': '#2196F3',
				shape: order.side == 'SELL' ? 'arrowDown' : 'arrowUp',
				text: `${order.side} # ${order.executedQty} $ ${order.price}`,
				size: 2,
			})
		}

		candleSeries.setMarkers(markers)

		// $("#contact_form").html("<div id='message'></div>");//arrowDown,belowBar
        // $("#message")
        //   .html("<h2>Contact Form Submitted!</h2>")
        //   .append("<p>We will be in touch soon.</p>")
        //   .hide()
        //   .fadeOut(1500, function () {
        //     $("#message").append(
        //       "<img id='checkmark' src='images/check.png' />"
        //     );
        //   });
      },
	  error: function(errorThrown) {
		console.log(errorThrown);
	  }
    });

    e.preventDefault();
});