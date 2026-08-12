import logging
from logging import StreamHandler
logger = logging.getLogger()
formatter = logging.Formatter(
    " %(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
def setup_logging():
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)