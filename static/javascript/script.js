$(document).ready(function() {
  if (!window.WebSocket) {
    alert("Browser don't support WebSocket!");
    return;
  }

  var protocol = "ws";
  if (location.protocol == "https:") {
    protocol = "wss";
  }
  var url = protocol + "://" + location.host + "/ws";
  console.log("[websocket] established url: " + url);
  var ws = new ReconnectingWebSocket(url);

  var photobooth;
  ws.onopen = function() {
    photobooth = $('#container').photobooth();


    photobooth.on('image', function(event, dataUrl) {
      $(".result_img").fadeOut(300).delay(500).remove();
      $(".status").attr("src", "/static/assets/swaping.gif");

      ws.onmessage = function(event) {
        var result = JSON.parse(event.data);
        if (result.action == "finish") {
          console.log("replace " + result.id);
          var id = result.id;
          var data = result.data;
          var container = ".lsti" + id;
          $(container + " .result_img").remove();
          $("<img />", {"src": result.data[i], "class": "result_img"}).appendTo($(container));
        } else {
          var newUrl = "/static/assets/" + result.status + ".gif";
          $('.status').attr("src", newUrl);
        }
      }

      var data = {"action": "query", "content": dataUrl};
      ws.send(JSON.stringify(data));

    });
  }

});
