from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.post("/trend")
async def get_trend_image():
    file_path = "/workspace/generated/trend.png"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    else:
        return Response(content="File not found", status_code=404)