$(document).ready(function() {
  var photobooth = $('#container').photobooth();

  if (!window.WebSocket) {
    alert("Browser don't support WebSocket!");
    return;
  }

  var lock = false;

  photobooth.on('image', function(event, dataUrl) {
    if (lock) {
      alert("Please don't send the duplicated request!")
    }

    lock = true;

    var protocol = "ws";
    if (location.protocol == "https:") {
      protocol = "wss";
    }
    var url = protocol + "://" + location.host + "/ws";
    console.log("[websocket] established url: " + url)
    var ws = new WebSocket(url);

    ws.onmessage = function(event) {
      var result = JSON.parse(event.data);
      if (result.action == "finish") {
        for (var i = 0; i < result.data.length; i++) {
          console.log("replace " + i);
          var container = ".lsti" + i;
          $("<img />", {src: result.data[i]}).appendTo($(container));
        }
        lock = false;
      } else {
        var newUrl = "/static/assets/" + result.status + ".gif";
        $('.status').attr("src", newUrl);
      }
    }

    var data = {"action": "query", "content": dataUrl};
    ws.onopen = function() {
      ws.send(JSON.stringify(data));
    }

  });

});
