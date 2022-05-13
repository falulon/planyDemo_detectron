from importlib.metadata import metadata
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2 import model_zoo

import asyncio
import cv2
import os
import gdown
import uvicorn
import sys
import numpy as np
import base64

#API
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from pathlib import Path

  
export_file_url = "https://drive.google.com/uc?id=1eymYxEE450VTMikB4VZLFgiMjgi2-3gN"  #model link on Gdrive 
export_file_name = 'model_final.pth'
is_model_configured = False

path=Path()
os.chdir("app")

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='static'))

async def load_model(url, dest):
    if dest.exists(): 
        print('download model SKIPPED. The model file exists at', dest)
    else:
        async def download_model():
            gdown.download(str(url), str(dest), quiet=False)
        print("Downloading model for the first time, it may take a while...")
        await download_model()
        print("Download Complete. 100% ")
    await setup_detectron()
    
async def setup_detectron(): 
    # setup cfg model
    cfg = get_cfg() 
    # cfgFile = "./server/mask_rcnn_R_101_FPN_3x.yaml"
    # cfg.merge_from_file(cfgFile)
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"))
    model_path = "./server/model_final.pth"  # use the trained model weights
    
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = model_path   
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 9
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.45
    global predictor

    predictor = DefaultPredictor(cfg)
    global is_model_configured
    is_model_configured = True
    print("detectron model is configured")

# set up the class names to present    
class Metadata:  
    categories = [
    { "id": 1, "name": "livingroom", "supercategory": "" },
    { "id": 2, "name": "bedroom", "supercategory": "" },
    { "id": 3, "name": "kitchen", "supercategory": "" },
    { "id": 4, "name": "bathroom", "supercategory": "" },
    { "id": 5, "name": "closet", "supercategory": "" },
    { "id": 6, "name": "generic_room", "supercategory": "" },
    { "id": 7, "name": "balcony_terrace", "supercategory": "" },
    { "id": 8, "name": "diningroom", "supercategory": "" },
    { "id": 9, "name": "foyer_hall", "supercategory": "" }
    ]

    def get(self, _):    
        categories_list = map((lambda cat: cat['name'].replace('_',' ').capitalize()), Metadata.categories)
        return list(categories_list)
 
    ## setup the visualizer. and produce the output image as a base64 to be sent back to client
def analyze_image(im): 
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1] , Metadata, scale=1)
    v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    
    pred_boxes = outputs['instances'].pred_boxes.tensor.tolist()
    # pred_scores =outputs['instances'].scores.tolist()
    return_img = v.get_image()
    image_as_string = base64.b64encode(cv2.imencode('.jpg', return_img)[1]).decode()
    return image_as_string, pred_boxes

# run detectron inference
@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = cv2.imdecode( np.asarray(bytearray(img_bytes), dtype=np.uint8), 1 )
    
    try:
        result, pred_boxes = analyze_image(img)
        return JSONResponse({'result': 'OK', 'image_data': result, 'xyxy': pred_boxes})
   
    except: 
        return JSONResponse({'result': str('error')})


## serve the home page 
@app.route('/')
async def homepage(request):
    if not is_model_configured:
        print('Detectron model is not configured')
        await load_model(export_file_url, path / 'server' / export_file_name) ##check if the model is loaded first
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())



if __name__ == '__main__':
    if 'serve' in sys.argv:
        port = int(os.environ.get('PORT', 5000))
        uvicorn.run(app=app, host='0.0.0.0', port=port, log_level="info")
        
asyncio.run(load_model(export_file_url, path / 'server' / export_file_name)) ## run 1st on server initialisation 



