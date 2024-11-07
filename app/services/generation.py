
from redis import Redis
from rq import Queue
from uuid import UUID, uuid4
from app.core.config import settings
from app.core.logging import logger
import json

class GenerationService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.queue = Queue('generation', connection=self.redis)

    async def create_image_task(self, prompt: str):
        try:
            task_id = str(uuid4())
            logger.info(f"Creating image task: {task_id} with prompt: {prompt}")
            
            self.redis.hset(
                f"task:{task_id}",
                mapping={
                    "status": "pending",
                    "type": "image",
                    "prompt": prompt
                }
            )
            
            # Set TTL for task data (24 hours)
            self.redis.expire(f"task:{task_id}", 86400)
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating image task: {e}")
            raise

    async def get_task_status(self, task_id: str):
        try:
            task_data = self.redis.hgetall(f"task:{task_id}")
            if not task_data:
                return None
                
            return {
                "status": task_data.get(b"status").decode(),
                "type": task_data.get(b"type").decode(),
                "result_path": task_data.get(b"result_path", b"").decode()
            }
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            raise