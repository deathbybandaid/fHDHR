import os
from collections import OrderedDict
import logging
from logging.config import dictConfig


from fHDHR.tools import isint


class MEMLogs():

    def __init__(self):
        self.dict = OrderedDict()


memlog = MEMLogs()


class MemLogger(logging.StreamHandler):
    level = 0

    def emit(self, record):

        if not len(list(memlog.dict.items())):
            record_number = 0
        else:
            record_number = max(list(memlog.dict.keys())) + 1

        memlog.dict[record_number] = {
                                      "fmsg": self.format(record)
                                      }

        for record_item in dir(record):
            if not record_item.startswith("__"):
                memlog.dict[record_number][record_item] = eval("record.%s" % record_item)


class Logger():
    LOG_LEVEL_CUSTOM_NOOB = 25
    LOG_LEVEL_CUSTOM_SSDP = 8

    def __init__(self, settings):
        self.config = settings
        self.custom_log_levels()
        logging.MemLogger = MemLogger
        logging_config = {
            'version': 1,
            'formatters': {
                'fHDHR': {
                    'format': '[%(asctime)s] %(levelname)s - %(message)s',
                    },
            },
            'loggers': {
                # all purpose, fHDHR root logger
                'fHDHR': {
                    'level': self.levelname,
                    'handlers': ['console', 'logfile', 'memlog'],
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
                        self.config.internal["paths"]["logs_dir"], '.fHDHR.log'),
                    'when': 'midnight',
                    'formatter': 'fHDHR',
                },
                # Memory Logging
                'memlog': {
                    'class': 'logging.MemLogger',
                    'formatter': 'fHDHR',
                }
            },
        }
        dictConfig(logging_config)
        self.logger = logging.getLogger('fHDHR')
        self.memory = memlog
        print(self.logger._levelNames)

    def get_levelno(self, level):
        if isint(level):
            return int(level)
        else:
            return self.fhdhr.logger.getLevelName(level.upper())

    def get_levelname(self, level):
        if isint(level):
            return self.fhdhr.logger.getLevelName(int(level))
        else:
            return level.upper()

    @property
    def levelno(self):
        if isint(self.config.dict["logging"]["level"]):
            return int(self.config.dict["logging"]["level"])
        else:
            return self.fhdhr.logger.getLevelName(self.config.dict["logging"]["level"].upper())

    @property
    def levelname(self):
        if isint(self.config.dict["logging"]["level"]):
            return self.fhdhr.logger.getLevelName(int(self.config.dict["logging"]["level"]))
        else:
            return self.config.dict["logging"]["level"].upper()

    def custom_log_levels(self):

        # NOOB Friendly Logging Between INFO and WARNING
        logging.addLevelName(self.LOG_LEVEL_CUSTOM_NOOB, "NOOB")
        logging.Logger.noob = self._noob

        # SSDP Logging Between DEBUG and NOTSET
        logging.addLevelName(self.LOG_LEVEL_CUSTOM_SSDP, "SSDP")
        logging.Logger.ssdp = self._ssdp

    def _noob(self, message, *args, **kws):
        if self.isEnabledFor(self.LOG_LEVEL_CUSTOM_NOOB):
            # Yes, logger takes its '*args' as 'args'.
            self._log(self.LOG_LEVEL_CUSTOM_NOOB, message, args, **kws)

    def _ssdp(self, message, *args, **kws):
        if self.isEnabledFor(self.LOG_LEVEL_CUSTOM_SSDP):
            # Yes, logger takes its '*args' as 'args'.
            self._log(self.LOG_LEVEL_CUSTOM_SSDP, message, args, **kws)

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        if hasattr(self.logger, name):
            return eval("self.logger.%s" % name)
        elif hasattr(self.logger, name.lower()):
            return eval("self.logger.%s" % name.lower())
