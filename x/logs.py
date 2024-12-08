import logging

from omlish import logs


log = logging.getLogger(__name__)


logs.configure_standard_logging('INFO')

log.info('hi')
