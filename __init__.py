import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='REST_API_LIB: %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)