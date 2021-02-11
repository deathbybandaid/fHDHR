import os
import logging


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
        self.config = settings

        log_level = self.config.dict["logging"]["level"].upper()

        # Create a custom logger
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=log_level)
        self.logger = logging.getLogger('fHDHR')
        log_file = os.path.join(self.config.internal["paths"]["logs_dir"], 'fHDHR.log')

        # Create handlers
        # c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file)
        # c_handler.setLevel(log_level)
        f_handler.setLevel(log_level)

        # Create formatters and add it to handlers
        # c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        # f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # c_handler.setFormatter(c_format)
        # f_handler.setFormatter(f_format)

        formatter = ColoredFormatter()
        f_handler.setFormatter(formatter)

        # Add handlers to the logger
        # logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

        self.logger.info("cyan")
        self.logger.warning("yellow")
        self.logger.error("red")
        self.logger.critical("bgred")
        self.logger.debug("bggrey")

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        if hasattr(self.logger, name):
            return eval("self.logger.%s" % name)
