
from ..function_registry import FunctionRegistry
from ..generation import GenerationService
from app.core.logging import logger

generation_service = GenerationService()

@FunctionRegistry.register(
    name="generate_image",
    description="Generate an image based on text description",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate"
            }
        },
        "required": ["prompt"]
    }
)
async def generate_image(prompt: str):
    try:
        logger.info(f"Generating image with prompt: {prompt}")
        task_id = await generation_service.create_image_task(prompt)
        logger.info(f"Created task with ID: {task_id}")
        return {
            "task_id": task_id,
            "message": f"Image generation task created with ID: {task_id}. You can check the status using this ID."
        }
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}")
        raise

@FunctionRegistry.register(
    name="check_generation_status",
    description="Check the status of a generation task",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "ID of the generation task to check"
            }
        },
        "required": ["task_id"]
    }
)
async def check_generation_status(task_id: str):
    try:
        logger.info(f"Checking status for task: {task_id}")
        status = await generation_service.get_task_status(task_id)
        if not status:
            return {"message": "Task not found"}
        logger.info(f"Task status: {status}")
        return status
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        raise