// convert unix_time to human time
function time(unix_time) {
    var date = new Date(unix_time*1000);
    return date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
}

document.addEventListener('DOMContentLoaded', function () {
    // popup modal windows
    var btns = document.querySelectorAll('a[data-toggle=modal]');
    for (i = 0; i < btns.length; i++) {
        var target_id = btns[i].getAttribute('href').replace('#', '');
        btns[i].onclick = function() {
            document.getElementById(target_id).style.display = 'block';
        }
    }
});