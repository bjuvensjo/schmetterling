import logging
from functools import wraps
from logging import FileHandler, Formatter, StreamHandler, getLogger
from os import makedirs
from sys import stdout


def log_params_return(level='info'):
    def wrap(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            try:
                value = f(*args, **kwargs)
                return value
            except Exception as e:
                value = e
                raise
            finally:
                log = getattr(getLogger(f.__module__), level)
                log('%s: %s %s\n=> %s', f.__name__, args, kwargs, value)

        return decorator

    return wrap


def create_console_handler(formatter):
    handler = StreamHandler(stdout)
    handler.setFormatter(formatter)
    return handler


def create_file_handler(log_dir, log_file, formatter):
    handler = FileHandler(f'{log_dir}/{log_file}.log')
    handler.setFormatter(formatter)
    return handler


def create_formatter():
    return Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')


def get_handlers(log_dir, log_file):
    formatter = create_formatter()
    return {
        'console_handler':
            create_console_handler(formatter),
        'file_handler':
            create_file_handler(
                log_dir,
                log_file,
                formatter,
            ),
    }


@log_params_return('debug')
def log_config(log_dir, name, level):
    makedirs(log_dir, exist_ok=True)

    log = getLogger()
    log.setLevel(getattr(logging, level))
    handlers = get_handlers(log_dir, name)
    log.handlers = list(handlers.values())
    return handlers
