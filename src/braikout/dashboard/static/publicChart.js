
var BITFINEX_COLOR = '#4995c4';
var BITSTAMP_COLOR = '#14A04B';

function createChart(chartName, symbol, data){
    return Highcharts.chart(chartName, {
        chart: {
            type: 'spline'
        },
        title: {
            text: symbol + ' Latest Prices'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                second: '%k:%M:%S',
            },
            title: {
                text: 'Timestamp (UTC)'
            },
            crosshair: true,
        },
        yAxis: {
            title: {
                text: 'Price'
            },
            labels: {
                align: 'left',
                x: -25,
                y: -1
            },
            opposite: true,
            showFirstLabel: false,
            tickPosition: 'inside'
        },
        legend: {
            enabled: false
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            spline: {
                marker: {
                    enabled: true
                }
            }
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '${point.y:.2f} @ {point.x:%k:%M:%S}'
        },
        series: [{
            name: 'Bitstamp',
            color: BITSTAMP_COLOR,
            data: data['Bitstamp']
        }, {
            name: 'Bitfinex',
            color: BITFINEX_COLOR,
            data: data['Bitfinex']
        }],
    });
}

$(document).ready(() => {
    var pusher = pusherConnect();
    var btcData = {
        'Bitstamp': [],
        'Bitfinex': []
    };
    var ethData = {
        'Bitstamp': [],
        'Bitfinex': []
    };
    var ltcData = {
        'Bitstamp': [],
        'Bitfinex': []
    };

    var btcChart;
    var ethChart;
    var ltcChart;
    if ($('#chart-btc').length) {
        btcChart = createChart('chart-btc', 'BTC', btcData);
    }
    if ($('#chart-eth').length) {
        ethChart = createChart('chart-eth', 'ETH', ethData);
    }
    if ($('#chart-ltc').length) {
        ltcChart = createChart('chart-ltc', 'LTC', ltcData);
    }

    var btcChannel = pusher.subscribe('prices__btc');
    var ethChannel = pusher.subscribe('prices__eth');
    var ltcChannel = pusher.subscribe('prices__ltc');
    var eurChannel = pusher.subscribe('prices__eur');

    var priceUpdateFunction = function(symbol, cryptoChart, cryptoData){
        return function(data) {
            if(!cryptoChart){
                return;
            }
            var series = 0;
            if (data.exchange === 'Bitfinex'){
                series = 1;
            }
            var price = [(new Date(data.timestamp)).getTime(), data.price];

            var $lastPrice = $('.js-price-' + symbol);
            $lastPrice.html(data.price)
            $lastPrice.trigger('priceUpdated', {
                'price': data.price
            })

            var chartData = cryptoData[data.exchange];
            chartData.push(price)
            if(chartData.length >= 10){
                chartData = chartData.slice(chartData.length - 10)
            }
            cryptoChart.series[series].update({data: chartData})
        }
    }

    btcChannel.bind('price', priceUpdateFunction('btc', btcChart, btcData));
    ethChannel.bind('price', priceUpdateFunction('eth', ethChart, ethData));
    ltcChannel.bind('price', priceUpdateFunction('ltc', ltcChart, ltcData));
    eurChannel.bind('price', priceUpdateFunction('eur', ltcChart, ltcData));
})