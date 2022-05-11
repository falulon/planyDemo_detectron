
// disable selection in DOM
const disableselect = (e) => false;  
document.onselectstart = disableselect;  



function dataURLtoBlob(dataurl) {
  var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
      bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
  while(n--){
      u8arr[n] = bstr.charCodeAt(n);
  }
  return new Blob([u8arr], {type:mime});
}

var el = x => document.getElementById(x);  //shortcut for getElementById

function showPicker() {
  el("file-input").click();
  el("result-label").classList.add('no-display');
}

// open the cropper once an image was chosen
function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    crop(e.target.result);
  };
  reader.readAsDataURL(input.files[0]);
}


async function analyze() {

  var croppedFile = await cropSave()  //get the cropped image
  var uploadFiles = [dataURLtoBlob(croppedFile)]; 

  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Detecting...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  
    xhr.onerror = function() {
    alert(xhr.responseText);
  };
  
  xhr.onload = function(e) {
    if (this.readyState === 4) {
      // el("result-label").innerHTML = `${response["result"]}`;
      el("result-label").classList.remove('no-display');
    }
    el("analyze-button").innerHTML = "Detect";
  };

 xhr.addEventListener("load", imageHandler);

function imageHandler() {
  const response = JSON.parse(this.responseText);
  const resultImage = el("result-image");
  resultImage.src = `data:image/png;base64, ${response["image_data"]}`;

  const showModal = () => {
  const content = document.querySelector('.content');
  const modal = el("result-modal")
  modal.showModal()
  content.style.visibility = "hidden"
  modal.addEventListener('click', (event)=>{
    if (event.target !== resultImage) {modal.close(); content.style.visibility = "visible"}});
  }

  showModal()
}

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);

  xhr.send(fileData);
}

