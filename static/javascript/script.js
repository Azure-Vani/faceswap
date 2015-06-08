$(document).ready(function() {
  var photobooth = $('#container').photobooth();
  photobooth.on('image', function(event, dataUrl) {
    var ajax = $.ajax({
      method: "POST",
      url: "/query",
      data: {"data": dataUrl}
    }).success(function(data) {
      $('#result').attr('src', dataUrl);
      alert("Transmission Successful!");
    }).fail(function() {
      alert("Transmission Failed!");
    });
  });
});
