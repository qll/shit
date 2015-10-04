import logging


def initialize(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(message)s')


def disable():
    do_nothing = lambda *s: None
    for func in ('debug', 'info', 'warning', 'error', 'exception'):
        globals()[func] = do_nothing


def debug(msg, *args, **kwargs):
    logging.debug('[DEBUG] %s' % msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logging.warning('[WARN] %s' % msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logging.error('[ERROR] %s' % msg, *args, **kwargs)


def exception(error, *args, **kwargs):
    logging.exception(error, *args, **kwargs)
