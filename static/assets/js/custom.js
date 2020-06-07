$(".custom-file-input").on("change", function () {
    var acceptedImgExt = ["jpg", "jpeg", "png", "gif"];
    var filePath = $(this).val();
    var fileName = filePath.split("\\").pop();
    var fileNameExt = fileName.split(".");
    var fileExt = fileNameExt[fileNameExt.length - 1].toLowerCase()
    if (acceptedImgExt.indexOf(fileExt) > -1) {
        $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
        try {
            document.getElementById('src-image').src = window.URL.createObjectURL(this.files[0]);
        } catch (error) {
            // do nothing  console.log(error)
        }
    } else {
        $("#src-image-text").text("Unacceptable file format! Expected JPG(JPEG), PNG OR GIF");
    }
});