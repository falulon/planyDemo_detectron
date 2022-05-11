var cropper; 
var squareSize = window.screen.width > window.screen.height ? 400 : 600   // cropper elenemnt size for portrait / landscape screens
function crop(location) {
    // remove exisiting before getting a new one 
    if (cropper) cropper.destroy();

    // set up the cropper element in the div
    cropper = new Croppie(document.getElementById('image'),{
        enableExif: true,
        enableResize: true,
        viewport: {
            width: squareSize,
            height: squareSize,
            // type: 'circle'
        },
        boundary: {
            width: squareSize+120,
            height: squareSize+80,
        }
    });

    // show the image 
    cropper.bind({
      url: location,
      orientation: 1
    });
}

  // save the selection and send it back to client.js
async function cropSave() { 
    var params = {type: 'base64', size: 'original', format: 'jpeg', quality: 1, circle: false }
    return await cropper.result(params);
 }
