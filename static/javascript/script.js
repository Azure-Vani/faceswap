$(document).ready(function() {
  var photobooth = $('#container').photobooth();
  photobooth.on('image', function(event, dataUrl) {
    $('#result').attr('src', dataUrl);
    var ajax = $.ajax({
      method: "POST",
      url: "/query",
      data: {"data": dataUrl}
    }).success(function() {
      alert("Transmission Successful!");
    }).fail(function() {
      alert("Transmission Failed!");
    });
  });
});
