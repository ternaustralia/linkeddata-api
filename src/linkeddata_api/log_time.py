import inspect
import logging
import time

from functools import wraps

logger = logging.getLogger(__name__)


def log_time(func):
    """This decorator prints the execution time for the decorated function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)

        logger.debug("Running %s", f"{info.filename}:{info.lineno}")

        start = time.time()
        try:
            result = func(*args, **kwargs)
            end = time.time()

            logger.debug(
                "%s ran in %ss",
                f"{info.filename}:{info.lineno}",
                round(end - start, 2),
            )
            return result
        except Exception as err:
            logger.error(
                "Error occurred running %s with args: %s kwargs: %s. Message: %s",
                f"{info.filename}:{info.lineno}",
                str(args),
                str(kwargs),
                err,
            )

            raise err

    return wrapper
