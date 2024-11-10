
from typing import Dict, Any, Callable, Optional
import inspect
import asyncio

class FunctionRegistry:
    _functions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, description: str, parameters: dict):
        def decorator(func: Callable):
            cls._functions[name] = {
                "function": func,
                "description": description,
                "parameters": parameters
            }
            return func
        return decorator

    @classmethod
    async def execute_function(cls, name: str, **kwargs) -> Any:
        if name not in cls._functions:
            raise ValueError(f"Function {name} not found")
        
        func = cls._functions[name]["function"]
        
        # Handle both async and sync functions
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return await asyncio.to_thread(func, **kwargs)

    @classmethod
    def get_function_descriptions(cls) -> list:
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in cls._functions.items()
        ]