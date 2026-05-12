"""
Configurazione centralizzata del logging per TrackerProxy
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Define log format
DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s'
SIMPLE_FORMAT = '%(message)s'

def setup_logging(log_level=logging.DEBUG):
    """
    Setup logging con output su console e file
    
    Args:
        log_level: Livello di logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(DETAILED_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler - Rotating log file
    file_handler = RotatingFileHandler(
        'logs/tracker_proxy.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)  # File always gets DEBUG level
    file_formatter = logging.Formatter(DETAILED_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # File handler - Error log
    error_handler = RotatingFileHandler(
        'logs/tracker_proxy_errors.log',
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(DETAILED_FORMAT)
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    # Get the main logger
    logger = logging.getLogger('[TrackerProxy]')
    logger.setLevel(log_level)
    
    return logger

# Quick setup
def quick_setup(debug=False):
    """Setup veloce per debug mode"""
    level = logging.DEBUG if debug else logging.INFO
    return setup_logging(level)
