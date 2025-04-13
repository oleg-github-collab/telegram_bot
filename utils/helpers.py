import logging
from config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)

def is_admin(user_id):
    """Перевірка чи користувач є адміністратором."""
    return user_id in ADMIN_USER_IDS

def setup_logger():
    """Налаштування логування."""
    from config import LOG_LEVEL

    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=numeric_level
    )