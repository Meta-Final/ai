import uvicorn
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

if __name__=='__main__':
       uvicorn.run(app, host = '0.0.0.0', port=9000)