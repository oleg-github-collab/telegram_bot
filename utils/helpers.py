import logging
from config import ADMIN_USER_IDS, LOG_LEVEL

def is_admin(user_id):
    return user_id in ADMIN_USER_IDS

def setup_logger():
    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=numeric_level
    )
