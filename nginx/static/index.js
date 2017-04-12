function validatePassword(evt) {
  evt.preventDefault();
  $.post("api/password", {"secret": $("#secret").val()}, function(response) {
    if (response.status == 0) {
      uploadFile();
    } else if (response.status == 1) {
      alert(response.error);
    }
  }, "json");
}

function uploadFile() {
  var formData = new FormData($("#file")[0]);
  var xhr = new XMLHttpRequest();
  xhr.upload.addEventListener("progress", function(evt) {
    if (evt.lengthComputable) {
      console.log(evt.loaded, evt.total);
      $("#progress").attr({
        value: evt.loaded,
        max: evt.total
      });
    }
  });

  xhr.addEventListener("load", function(evt) {
    if (this.status == 200) {
      var response = JSON.parse(this.responseText);
      if (response.status == 0) {
        window.location.href += response.uploaded_name;
      } else if (response.status == 1) {
        alert(response.error);
      }
    }
  });

  xhr.open("POST", "api/upload");
  xhr.send(formData);
}

$(function() {
  $("#file").submit(validatePassword);
})
