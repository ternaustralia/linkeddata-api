import inspect
import logging
import time

from functools import wraps

logger = logging.getLogger(__name__)


def log_time(func):
    """This decorator prints the execution time for the decorated function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)

        logger.debug(
            "%s ran in %ss",
            f"{info.filename}:{info.lineno}",
            round(end - start, 2),
        )
        return result

    return wrapper
