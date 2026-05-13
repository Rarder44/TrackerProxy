"""
Configurazione centralizzata del logging per TrackerProxy
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
import io

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
    
    # Console handler (stdout) with proper encoding for Windows
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(DETAILED_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # Fix encoding for Windows console (UTF-8 support)
    if sys.stdout.encoding != 'utf-8':
        # Wrap stdout to handle UTF-8 even on Windows
        try:
            console_handler.stream = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                write_through=True
            )
        except (AttributeError, TypeError):
            # Fallback: just use what we have
            pass
    
    root_logger.addHandler(console_handler)
    
    # File handler - Rotating log file (with UTF-8 encoding)
    file_handler = RotatingFileHandler(
        'logs/tracker_proxy.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # File always gets DEBUG level
    file_formatter = logging.Formatter(DETAILED_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # File handler - Error log (with UTF-8 encoding)
    error_handler = RotatingFileHandler(
        'logs/tracker_proxy_errors.log',
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
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
