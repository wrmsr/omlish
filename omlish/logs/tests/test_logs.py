import logging

from .. import formatters
from .. import configs


def test_logs():
    for f in [
        formatters.ColorLogFormatter(configs.build_log_format(configs.STANDARD_LOG_FORMAT_PARTS)),
        formatters.JsonLogFormatter(),
    ]:
        handler = logging.StreamHandler()
        handler.setFormatter(f)

        log = logging.getLogger('_test')
        log.handlers.clear()
        log.handlers.append(handler)
        log.setLevel(logging.INFO)

        print()
        log.info('hi')
        log.warning('hi')
        log.error('hi')
