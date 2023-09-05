
document.addEventListener('DOMContentLoaded', () => {
    var logDataDiv = document.getElementById('sse-data');
    var eventSource = new EventSource('/stream_log');

    eventSource.onmessage = function (event) {
        // Append new log data to the existing content
        logDataDiv.innerHTML += event.data + '<br>';
        //$('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    };
});