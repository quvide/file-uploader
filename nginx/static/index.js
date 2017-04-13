var fileSelected = false;
var passwordOk = false;

function updateButtonStatus() {
  if (fileSelected && passwordOk) {
    $("#upload").slideDown();
  } else {
    $("#upload").slideUp();
  }
}

function updateTimeStatus() {
  if (passwordOk) {
    $("#time-container").slideDown();
  } else {
    $("#time-container").slideUp();
  }
}

function validatePassword(evt) {
  $.post("api/password", {"secret": $("#secret").val()}, function(response) {
    $("#secret").removeClass();
    if (response.status == 0) {
      passwordOk = true;
      $("#secret").addClass("green");
    } else if (response.status == 1) {
      passwordOk = false;
      $("#secret").addClass("red");
    } else if (response.status == 2) {
      passwordOk = true;
    }
    $("#time").attr({"placeholder": response.max_time, "max": response.max_time});
    updateButtonStatus();
    updateTimeStatus();
  }, "json");
}

function uploadFile(evt) {
  evt.preventDefault();

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

  $("#progress").slideDown();

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

function showFile(evt) {
  $("#file-label").text("File selected");
  fileSelected = true;
  updateButtonStatus();
}

$(function() {
  $("#file").on("submit", uploadFile);
  $("#file-input").on("change", showFile);
  $("#secret").on("input", validatePassword);
  validatePassword();
})
