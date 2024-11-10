
from ..function_registry import FunctionRegistry

@FunctionRegistry.register(
    name="calculate",
    description="Perform basic arithmetic calculations",
    parameters={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "The arithmetic operation to perform"
            },
            "x": {
                "type": "number",
                "description": "First number"
            },
            "y": {
                "type": "number",
                "description": "Second number"
            }
        },
        "required": ["operation", "x", "y"]
    }
)
async def calculate(operation: str, x: float, y: float):
    operations = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "divide": lambda a, b: a / b if b != 0 else "Cannot divide by zero"
    }
    return str(operations[operation](x, y))