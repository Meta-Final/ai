import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import FileResponse

app = FastAPI()

@app.get('/thumbnail')
async def cover():
    img_path = './1.png'
    return FileResponse(img_path, media_type='image/png')

@app.get('/trend')
async def trend():
    img_path = './trend.png'
    return FileResponse(img_path, media_type='image/png')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=14596)