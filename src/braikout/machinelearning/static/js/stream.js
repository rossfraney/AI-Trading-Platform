Pusher.logToConsole = true;
var pusher = new Pusher('de504dc5763aeef9ff52');
var channel = pusher.subscribe('live_trades');
channel.bind('trade', function (data) {
    console.log(data)
    document.getElementById("btcprice").innerHTML = "BTC: " + data.price_str;
});
channel.bind('pusher:subscription_succeeded', function (data) {
    console.log("Subscribed correctly BTC")
});
var channel2 = pusher.subscribe('live_trades_ltcusd');
channel2.bind('trade', function (data) {
    console.log(data)
    document.getElementById("ltcprice").innerHTML = "LTC: " + data.price_str;
});
channel2.bind('pusher:subscription_succeeded', function (data) {
    console.log("Subscribed correctly LTC")
});
var channel3 = pusher.subscribe('live_trades_ethusd');
channel3.bind('trade', function (data) {
    console.log(data)
    document.getElementById("ethprice").innerHTML = "ETH: " + data.price_str;
});
channel3.bind('pusher:subscription_succeeded', function (data) {
    console.log("Subscribed correctly ETH")
});
var channel4 = pusher.subscribe('live_trades_eurusd');
channel4.bind('trade', function (data) {
    console.log(data)
    document.getElementById("eurprice").innerHTML = "EUR: " + data.price_str;
});
channel4.bind('pusher:subscription_succeeded', function (data) {
    console.log("Subscribed correctly EUR")
});
//    var channel2 = pusher.subscribe('live_ticker');
//    var channel3 = pusher.subscribe('live_tickers');
// var channel4 = pusher.subscribe('prices__btc');