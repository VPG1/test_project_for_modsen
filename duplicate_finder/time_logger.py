import loguru
import time


def time_logger(function):
    def wrapped(*args):
        start_time = time.time()
        res = function(*args)
        loguru.logger.info(f'Время выполнения: {time.time() - start_time} sec')
        return res

    return wrapped
