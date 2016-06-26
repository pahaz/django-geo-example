window.onload = function () {
    window.socket = new SocketHandler('messages', function (msg) {
        console.log(msg);
        if (msg.text && msg.created) {
            $('.messages').prepend(
                '<h4 class="well"><strong>' + msg.text + '</strong> - <em>' + msg.created + '</em></h4>'
            )
        }
    });
};

var SocketHandler = function (channel, onMessage, onOpen, onClose) {
    var uuid = Math.random().toString(36).substring(7);
    var url = "ws://localhost:8080/realtime/" + uuid + '/' + channel + '/';
    var sock = new WebSocket(url);

    sock.onopen = function () {
        console.log('open');
        onOpen && onOpen();
    };

    sock.onmessage = function (event) {
        var message = JSON.parse(event.data);
        onMessage(message);
    };

    sock.onclose = function (event) {
        console.log('close!');
        onClose && onClose();
    };

    this.send = function (message) {
        if (typeof message === 'object') {
            sock.send(JSON.stringify(message));
        } else {
            throw new Error('bad message');
        }
    };
};
