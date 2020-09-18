var pusherConnect = (function () {

    Pusher.logToConsole = true;

    var _pusher;
    return function(){

        if (_pusher){
            return _pusher
        }
        _pusher = new Pusher('de504dc5763aeef9ff52', {
            encrypted: true,
            cluster: 'mt1'
        });
        return _pusher;
    }
})();