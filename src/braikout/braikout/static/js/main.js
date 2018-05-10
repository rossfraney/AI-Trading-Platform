var wsaddr = window.location.host;
var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
var path = window.location.pathname.replace(/\/$/, "");
var wsUri = ws_scheme + "://" + wsaddr + path + "/ws/";
var websocket;
var svg;

function setupWebSocket() {
    websocket = new WebSocket(wsUri);
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
}

function onOpen (evt) {
    console.log("Connected to websocket!");
}

function onMessage (evt) {
    console.log("BTCCCCCCCCCCCCCCCCCCCCCC");
    var data = JSON.parse(evt.data);

    if (data.BTC) {
        $('.bitcoin-price')[0].innerHTML =  '$' + String(data.BTC);
    } else {
        $('.litecoin-price')[0].innerHTML =  '$' + String(data.LTC);

    }

}

$(".change-coin-js").click(function (e) {
    if ($(".wrapper-bitcoin").css("display") == "none") {
        $(".wrapper-bitcoin").css("display", "block");
        $(".wrapper-litecoin").css("display", "none");

        $(".change-coin-js")[0].innerHTML = "Change to litecoin";

        websocket.send(JSON.stringify({
            coin: 'bitcoin'
        }))
    } else if ($(".wrapper-litecoin").css("display") == "none") {
        $(".wrapper-litecoin").css("display", "block");
        $(".wrapper-bitcoin").css("display", "none");

        $(".change-coin-js")[0].innerHTML = "Change to bitcoin";

        websocket.send(JSON.stringify({
            coin: 'litecoin'
        }))
    }

});

window.addEventListener("load", setupWebSocket, false);