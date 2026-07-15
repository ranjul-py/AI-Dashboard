import logging
import os

def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a logger for application modules."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Consol handler
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        
        logger.addHandler(c_handler)
        
    return logger
