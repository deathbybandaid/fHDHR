import os
import logging
from logging.config import dictConfig


class Color(object):
    """
     utility to return ansi colored text.
    """

    colors = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'bgred': 41,
        'bggrey': 100
    }

    prefix = '\033['

    suffix = '\033[0m'

    def colored(self, text, color=None):
        if color not in self.colors:
            color = 'white'

        clr = self.colors[color]
        return (self.prefix+'%dm%s'+self.suffix) % (clr, text)


colored = Color().colored


class ColoredFormatter(logging.Formatter):

    def format(self, record):

        message = record.getMessage()

        mapping = {
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bgred',
            'DEBUG': 'bggrey'
        }

        clr = mapping.get(record.levelname, 'white')

        return colored(record.levelname, clr) + ': ' + message


class Logger():

    def __init__(self, settings):
        logging_config = {
            'version': 1,
            'formatters': {
                'fHDHR': {
                    '()': 'ColoredFormatter',
                    'format': '%(log_color)s[%(asctime)s] %(name)-20s %(levelname)-8s - %(message)s'
                    },
            },
            'loggers': {
                # all purpose, fHDHR root logger
                'fHDHR': {
                    'level': settings.dict["logging"]["level"].upper(),
                    'handlers': ['console', 'logfile'],
                },
            },
            'handlers': {
                # output on stderr
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'fHDHR',
                },
                # generic purpose log file
                'logfile': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': os.path.join(
                        settings.internal["paths"]["logs_dir"], '.fHDHR.log'),
                    'when': 'midnight',
                    'formatter': 'fHDHR',
                },
            },
        }
        dictConfig(logging_config)
        self.logger = logging.getLogger('fHDHR')

        self.logger.info("cyan")
        self.logger.warning("yellow")
        self.logger.error("red")
        self.logger.critical("bgred")
        self.logger.debug("bggrey")

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        if hasattr(self.logger, name):
            return eval("self.logger.%s" % name)
