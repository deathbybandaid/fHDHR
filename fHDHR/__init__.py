# coding=utf-8

from .device import fHDHR_Device
from .api import fHDHR_API_URLs

import fHDHR.tools
fHDHR_VERSION = "v0.9.0-beta"


class fHDHR_INT_OBJ():

    def __init__(self, settings, logger, db, plugins, versions):
        self.version = fHDHR_VERSION
        self.versions = versions
        self.config = settings
        self.logger = logger
        self.db = db
        self.plugins = plugins

        self.logger.debug("Setting Up shared Web Requests system.")
        self.web = fHDHR.tools.WebReq()
        for plugin_name in list(self.plugins.plugins.keys()):
            self.plugins.plugins[plugin_name].plugin_utils.web = self.web

        self.api = fHDHR_API_URLs(settings, self.web, versions, logger)
        for plugin_name in list(self.plugins.plugins.keys()):
            self.plugins.plugins[plugin_name].plugin_utils.api = self.api

        self.threads = {}


class fHDHR_OBJ():

    def __init__(self, settings, logger, db, plugins, versions):
        logger.info("Initializing fHDHR Core Functions.")
        self.fhdhr = fHDHR_INT_OBJ(settings, logger, db, plugins, versions)

        self.fhdhr.origins = fHDHR.origins.Origins(self.fhdhr)

        self.device = fHDHR_Device(self.fhdhr, self.fhdhr.origins)

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        if hasattr(self.fhdhr, name):
            return eval("self.fhdhr.%s" % name)
        elif hasattr(self.fhdhr.device, name):
            return eval("self.fhdhr.device.%s" % name)
