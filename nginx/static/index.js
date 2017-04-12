function uploadFile(evt) {
	evt.preventDefault();
	var formData = new FormData($("#file")[0]);
  var xhr = new XMLHttpRequest();
	xhr.addEventListener("progress", function(evt) {
		if (evt.lengthComputable) {
			$("#progess").attr({
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

	xhr.open("POST", "upload");
	xhr.send(formData);
}

$(function() {
	$("#file").submit(uploadFile);
})
