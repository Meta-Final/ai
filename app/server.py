import os
import uvicorn
import json
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post('/chat')
async def chat(text:dict=Body(...)):
    req = text.get('text')
    if req == '요리 이미지 만들어줘':
        res_path = '/img.json'
        return JSONResponse(content={'text':res_path})
    elif req == '작업한 포스트 내용을 오브젝트로 만들어줘':
        res_path = '/object.json'
        return JSONResponse(content={'text':res_path})

@app.get('/trend')
async def trend():
    trend_path = os.path.join(os.path.dirname(__file__), 'trend.json')
    
    with open(trend_path, 'r', encoding='utf-8') as f:
        trend_data = json.load(f)
        
    return JSONResponse(content={'trend':trend_data['trend']})

if __name__=='__main__':
       uvicorn.run(app, host='0.0.0.0', port=9000)