import loguru
import time


def time_logger(function):
    def wrapped(*args, **kwargs):
        loguru.logger.info("Function start.")
        start_time = time.time()
        res = function(*args, **kwargs)
        loguru.logger.debug(f'Execution time: {time.time() - start_time} sec.')
        return res

    return wrapped
