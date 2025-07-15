import logging
import json
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logger(name="AsyncBitcoinNodeMonitor", log_file="node_monitor_async.log"):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else '.'
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=14,
        encoding='utf-8',
        delay=False,
        utc=False
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    def format_message(*args):
        formatted_args = []
        for arg in args:
            if isinstance(arg, dict):
                formatted_args.append(json.dumps(arg, indent=2))
            else:
                formatted_args.append(str(arg))
        return " ".join(formatted_args)

    def debug_with_format(*args, exc_info=None):
        message = format_message(*args)
        logger.debug(message, exc_info=exc_info)

    def info_with_format(*args, exc_info=None):
        message = format_message(*args)
        logger.info(message, exc_info=exc_info)

    def warning_with_format(*args, exc_info=None):
        message = format_message(*args)
        logger.warning(message, exc_info=exc_info)

    def error_with_format(*args, exc_info=None):
        message = format_message(*args)
        logger.error(message, exc_info=exc_info)

    def critical_with_format(*args, exc_info=None):
        message = format_message(*args)
        logger.critical(message, exc_info=exc_info)

    logger.debugf = debug_with_format
    logger.infof = info_with_format
    logger.warningf = warning_with_format
    logger.errorf = error_with_format
    logger.criticalf = critical_with_format

    return logger


logger = setup_logger()