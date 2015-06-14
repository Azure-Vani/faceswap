$(document).ready(function() {
  var photobooth = $('#container').photobooth();
  photobooth.on('image', function(event, dataUrl) {
    var ajax = $.ajax({
      method: "POST",
      url: "/query",
      data: {"data": dataUrl}
    }).success(function(_data) {
      var data = eval(_data);
      for (var i = 0; i < 6; i++) {
        var listName = ".lsti" + i;
        $('<img />', {src: data[i]}).appendTo($(listName));
      }
      alert("Transmission Successful!");
    }).fail(function() {
      alert("Transmission Failed!");
    });
  });
});
