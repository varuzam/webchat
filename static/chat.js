function sendNotification(title, options) {
    // Проверим, есть ли права на отправку уведомлений
    if (Notification.permission === "granted") {
        // отправим уведомление
        var notification = new Notification(title, options);
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission(function (permission) {
            if (permission === "granted") {
                var notification = new Notification(title, options);
            }
        });
    }
}

var splited_url =  document.location.pathname.split('/');
var room_id = splited_url[splited_url.length - 1];

var socket = io.connect(document.location.origin);
socket.on('connect', function() {
    socket.emit('join', { "room_id": room_id });
});
socket.on('disconnect', function() {
    socket.emit('leave', { "room_id": room_id });
});
socket.on('message', function(data) {
    // don't notify myself
    if (data['user_sid'] !== socket.id) {
        sendNotification(data['user'], { body: data['msg'], dir: 'auto' });
    }
    document.getElementById('messages').innerHTML += '<li class="list-group-item"><i>(' + time(data['time']) + ')</i><b>' + data['user'] + '</b>: ' + data['msg'] + '</li>';
});

document.addEventListener('DOMContentLoaded', function () {
    // send message on clicking Send button
    document.getElementById('sendMsgBtn').addEventListener('click', function() {
        var msgInput = document.getElementById('msgInput');
        socket.emit('message', {"room_id": room_id, "msg": msgInput.value});
        msgInput.value = '';
    });
    // click Send button when Enter is pressed
    document.getElementById("msgInput").addEventListener("keyup", function(event) {
        event.preventDefault(); // Cancel the default action, if needed
        if (event.keyCode === 13) {
            document.getElementById("sendMsgBtn").click();
        }
    });
    // set active room_id in chat list
    document.getElementById('chatlist').querySelector('a[room_id="'+ room_id +'"]').classList.add('active');
});






