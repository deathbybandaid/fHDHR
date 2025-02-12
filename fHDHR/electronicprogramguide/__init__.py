
from .epg_handler import EPG_Handler


class EPG_Handlers():
    """
    fHDHR Electronic Program Guide system. (EPG)
    """

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.epg_handlers_dict = {}

        self.selfadd_epg_handlers()

        print(list_epg_handlers)

    @property
    def list_epg_handlers(self):
        return [epg_handler_name for epg_handler_name in list(self.epg_handlers_dict.keys())]

    @property
    def count_epg_handlers(self):
        return len(self.list_epg_handlers)

    @property
    def first_epg_handler(self):
        if self.count_epg_handlers:
            return self.list_epg_handlers[0]
        return None

    def get_epg_handler_obj(self, epg_handler_name):
        if epg_handler_name not in self.list_epg_handlers:
            return None
        return self.epg_handlers_dict[epg_handler_name]

    def get_epg_handler_conf(self, epg_handler_name):
        conf_dict = {}
        if epg_handler_name not in self.list_epg_handlers:
            return conf_dict
        return self.epg_handlers_dict[epg_handler_name].get_epg_handler_conf()

    def get_epg_handler_property(self, epg_handler_name, epg_handler_attr):
        if epg_handler_name not in self.list_epg_handlers:
            return None
        return self.epg_handlers_dict[epg_handler_name].get_epg_handler_property(epg_handler_attr)

    def epg_handler_has_method(self, epg_handler_name, epg_handler_attr):
        if epg_handler_name not in self.list_epg_handlers:
            return None
        return self.epg_handlers_dict[epg_handler_name].has_method(epg_handler_attr)

    def selfadd_epg_handlers(self):
        """
        Import EPG_Handlers.
        """
        print("--------------------------------------------------")

        self.fhdhr.logger.info("Detecting and Opening any found epg_handler plugins.")
        for plugin_name in self.fhdhr.plugins.search_by_type("alt_epg"):

            plugin = self.fhdhr.plugins.plugins[plugin_name]
            method = plugin.name.lower()
            self.fhdhr.logger.info("Found EPG_Handler: %s" % method)
            self.epg_handlers_dict[method] = EPG_Handler(self.fhdhr, plugin)

        print("--------------------------------------------------")
