import logging
import json
import os
import datetime
from termcolor import colored

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

import socket
import uuid

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "pid": os.getpid(),
            "host": socket.gethostname()
        }
        # Add extra fields if available
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)
        
        # Add stack trace if exception
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        # Schema Validation
        required_fields = ["log_id", "timestamp", "level", "message", "logger"]
        for field in required_fields:
            if field not in log_record:
                log_record[field] = "UNKNOWN"
        
        return json.dumps(log_record)

def setup_logger(name=None, log_file="logs/trading.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # File Handler (JSON)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    # Console Handler (Human Readable)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

def get_logger(name="TradingAgent"):
    return logging.getLogger(name)
