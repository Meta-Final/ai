import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# import logging
# from typing import Any
# import json
# from datetime import datetime

# class CustomFormatter(logging.Formatter):
#     def format(self, record: logging.LogRecord) -> str:
#         # Add timestamp and request_id if available
#         record.timestamp = datetime.utcnow().isoformat()
        
#         # Format extra fields
#         if hasattr(record, 'extra'):
#             record.extra = json.dumps(record.extra)
        
#         return super().format(record)

# def setup_logging() -> logging.Logger:
#     logger = logging.getLogger("llm_api")
#     logger.setLevel(logging.INFO)

#     # Console handler
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.INFO)
    
#     # Custom formatter
#     formatter = CustomFormatter(
#         '%(timestamp)s - %(levelname)s - %(name)s - %(message)s'
#     )
#     console_handler.setFormatter(formatter)
    
#     logger.addHandler(console_handler)
#     return logger

# logger = setup_logging()