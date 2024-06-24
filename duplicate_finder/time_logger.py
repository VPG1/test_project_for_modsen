import loguru
import time


def time_logger(function):
    def wrapped(*args):
        loguru.logger.info("Поиск дубликатов начался.")
        start_time = time.time()
        res = function(*args)
        loguru.logger.debug(f'Время выполнения: {time.time() - start_time} sec.')
        return res

    return wrapped
