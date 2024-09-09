"""
Logger configuration
"""
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='w')
    ]
)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a module name configured logger
    """
    return logging.getLogger(name)
