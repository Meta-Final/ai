import websocket
import uuid
import json
import urllib.request
import urllib.parse
import comfy_connect
import os

cf = comfy_connect

def make_magazine_cover(id, text):
    
    output_folder = f'./{id}/magazine_cover'
    
    with open('/magazine_api.json', 'r', encoding='utf-8') as f:
        prompt_text = f.read()

    prompt = json.loads(prompt_text)
    #set the text prompt for our positive CLIPTextEncode
    prompt['6']['inputs']['text'] = 'magazine_cover, magazine_style about' + text

    #set output file name
    prompt['9']['inputs']['filename_prefix'] = f'{id}'
    
    #set the seed for our KSampler node
    prompt['3']['inputs']['seed'] = 5

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(cf.server_address, cf.client_id))
    images = cf.get_images(ws, prompt)
    ws.close()
    
    for node_id in images:
        for image_data in images[node_id]:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            image.save(output_folder)    

