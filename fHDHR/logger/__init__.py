import os
from collections import OrderedDict
import logging
from logging.config import dictConfig


from fHDHR.tools import isint, closest_int_from_list


"""
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__',
'__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',

'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 'getMessage', 'levelname', 'levelno', 'lineno',
'message', 'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
'stack_info', 'thread', 'threadName']
"""


def sorted_levels(method):
    level_guide = {}
    sorted_levels = sorted(logging._nameToLevel, key=lambda i: (logging._nameToLevel[i]))
    if method == "name":
        for level in sorted_levels:
            level_guide[level] = logging._nameToLevel[level]
    elif method == "number":
        for level in sorted_levels:
            level_guide[logging._nameToLevel[level]] = level
    else:
        return logging._nameToLevel
    return level_guide


class MEMLogs():

    def __init__(self):
        self.dict = OrderedDict()
        self.logger = None

    def filter_by_level(self, level):
        returndict = OrderedDict()
        if isint(level):
            levels = sorted_levels("number")
            if level in list(levels.keys()):
                level = int(level)
            else:
                level = closest_int_from_list(list(levels.keys()), int(level))
        else:
            levels = sorted_levels("name")
            if level not in levels:
                level = self.logger.levelname
            level = logging.getLevelName(level.upper())

        for log_entry in list(self.dict.keys()):
            if self.dict[log_entry]["levelno"] >= level:
                returndict[log_entry] = self.dict[log_entry]
        return returndict


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
        self.memory.logger = self.logger

    def get_levelno(self, level):
        if isint(level):
            levels = sorted_levels("number")
            if level in list(levels.keys()):
                return int(level)
            else:
                return closest_int_from_list(list(levels.keys()), int(level))
        else:
            levels = sorted_levels("name")
            if level not in levels:
                level = self.levelname
            return logging.getLevelName(level.upper())

    def get_levelname(self, level):
        if isint(level):
            levels = sorted_levels("number")
            if level in list(levels.keys()):
                level = int(level)
            else:
                level = closest_int_from_list(list(levels.keys()), int(level))
            return logging.getLevelName(int(level))
        else:
            levels = sorted_levels("name")
            if level.upper() not in levels:
                level = self.levelname
            return level.upper()

    @property
    def levelno(self):
        if isint(self.config.dict["logging"]["level"]):
            levels = sorted_levels("number")
            if self.config.dict["logging"]["level"] in list(levels.keys()):
                return int(self.config.dict["logging"]["level"])
            else:
                return closest_int_from_list(list(levels.keys()), int(self.config.dict["logging"]["level"]))
        else:
            levels = sorted_levels("name")
            level = self.config.dict["logging"]["level"].upper()
            if self.config.dict["logging"]["level"].upper() not in levels:
                level = self.fhdhr.config.conf_default["logging"]["level"]["value"]
            return logging.getLevelName(level)

    @property
    def levelname(self):
        if isint(self.config.dict["logging"]["level"]):
            levels = sorted_levels("number")
            if self.config.dict["logging"]["level"] in list(levels.keys()):
                level = int(self.config.dict["logging"]["level"])
            else:
                level = closest_int_from_list(list(levels.keys()), int(self.config.dict["logging"]["level"]))
            return logging.getLevelName(level)
        else:
            levels = sorted_levels("name")
            level = self.config.dict["logging"]["level"].upper()
            if self.config.dict["logging"]["level"].upper() not in levels:
                level = self.fhdhr.config.conf_default["logging"]["level"]["value"]
            return level

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
