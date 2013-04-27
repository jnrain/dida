
var showNotification=true, notificationTimer=null, oldTitle, blinkFlag;
var heartbeatTimer=null;

// page visibility api
var hidden, visibilityChange;

if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support
  hidden = "hidden";
  visibilityChange = "visibilitychange";
} else if (typeof document.mozHidden !== "undefined") {
  hidden = "mozHidden";
  visibilityChange = "mozvisibilitychange";
} else if (typeof document.msHidden !== "undefined") {
  hidden = "msHidden";
  visibilityChange = "msvisibilitychange";
} else if (typeof document.webkitHidden !== "undefined") {
  hidden = "webkitHidden";
  visibilityChange = "webkitvisibilitychange";
}

function onVisibilityChange() {
  if (document[hidden]) {
    showNotification = true;
  } else {
    showNotification = false;
  }
}

// socket.io specific code
var socket = io.connect();

$(window).bind("beforeunload", function() {
    if (heartbeatTimer !== null) {
      clearInterval(heartbeatTimer);
    }

    socket.disconnect();
});

socket.on('connect', function () {
    $('#chat').addClass('connected');
});

socket.on('announcement', function (msg, timestamp) {
    var dt = new Date(timestamp * 1000);

    $('#lines').append(
      $('<p>')
      .append($('<time>').text(strdate(dt)))
      .append($('<em>').text(msg))
      );
    scrollMessages();
});

socket.on('nicknames', function (nicknames) {
    $('#nicknames').empty().append($('<span>在线: </span>'));
    for (var i in nicknames) {
	  $('#nicknames').append($('<b>').text(nicknames[i]));
    }
});

socket.on('msg_to_room', message);

socket.on('reconnect', function () {
    $('#lines').remove();
    message('系统', '已经重新连接');
});

socket.on('reconnecting', function () {
    message('系统', '尝试重新连接……');
});

socket.on('error', function (e) {
    message('系统', e ? e : '发生了未知错误');
});

function do_notify() {
  if (showNotification) {
    $('title').text((blinkFlag ? '【新消息】' : '【　　　】') + oldTitle);
    blinkFlag = !blinkFlag;
  } else {
    clearInterval(notificationTimer);
    notificationTimer = null;
  }
}

function zerofill2(i) {
  return (i >= 10) ? ('' + i) : ('0' + i);
}

function strdate(dt) {
  return (
      dt.getFullYear()
      + '/' + zerofill2(dt.getMonth() + 1)
      + '/' + zerofill2(dt.getDate())
      + ' ' + zerofill2(dt.getHours())
      + ':' + zerofill2(dt.getMinutes())
      + ':' + zerofill2(dt.getSeconds())
      );
}

function scrollMessages() {
  $('#lines').get(0).scrollTop = 10000000;
}

function doHeartbeat() {
  return socket.emit('heartbeat');
}

function message (from, msg, timestamp) {
    // console && console.log(from + ' ' + timestamp + ' ' + msg);
    var dt = new Date(timestamp * 1000);

    $('#lines').append(
      $('<p>')
      .append($('<time>').text(strdate(dt)))
      .append($('<b>').text(from !== null ? from : '我说'))
      .append($('<span>').text(msg))
    );
    scrollMessages();

    // notification
    if (showNotification) {
      if (notificationTimer !== null) {
        clearInterval(notificationTimer);
      }
      blinkFlag = false;
      notificationTimer = setInterval(do_notify, 800);
    }
}

// DOM manipulation
$(function () {
  if (typeof document.addEventListener === 'undefined' || typeof hidden === 'undefined') {
    // no
  } else {
    document.addEventListener(visibilityChange, onVisibilityChange, false);
  }

  oldTitle = $('title').text();

  // clear notification status on window focus
  $(window).focus(function() {
    if (notificationTimer !== null) {
      clearInterval(notificationTimer);
      notificationTimer = null;
    }

    $('title').text(oldTitle);
  });

  $('#set-nickname').submit(function (ev) {
    $('#login-err').css('visibility', 'hidden');
    $('#duplogin-err').css('visibility', 'hidden');

    socket.emit('login', {username: $('#username').val(), psw: $('#passwd').val()}, function (set) {
      if (!set) {
        clear();

        // start heartbeating
        if (heartbeatTimer === null) {
          heartbeatTimer = setInterval(doHeartbeat, 30000);
        }

        return $('#chat').addClass('nickname-set');
      }
      if (set == 1) {
        $('#login-err').css('visibility', 'visible');
      }
      if (set == 2) {
        $('#duplogin-err').css('visibility', 'visible');
      }
    });
    return false;
  });

  $('#send-message').submit(function () {
    var txt = $('#message').val();
    if (txt.trim().length == 0) {
      // no empty messages
      return false;
    }

    message(null, $('#message').val(), new Date().getTime() / 1000);
    socket.emit('user message', $('#message').val());
    clear();
    scrollMessages();
    return false;
  });

  function clear () {
    $('#message').val('').focus();
  };
});
