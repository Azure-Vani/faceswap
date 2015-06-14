$(document).ready(function() {
  var photobooth = $('#container').photobooth();
  photobooth.on('image', function(event, dataUrl) {
    var ajax = $.ajax({
      method: "POST",
      url: "/query",
      data: {"data": dataUrl}
    }).success(function(_data) {
      var data = eval(_data);
      var res = $('#result');
      for (var i = 0; i < 6; i++) {
        $('<img />', {src: data[i]}).appendTo(res);
      }
      alert("Transmission Successful!");
    }).fail(function() {
      alert("Transmission Failed!");
    });
  });
});
