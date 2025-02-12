
from .epg_handler import EPG_Handler


class EPG_Handlers():
    """
    fHDHR Electronic Program Guide system. (EPG)
    """

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.epg_handlers_dict = {}

        self.selfadd_epg_handlers()

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
            self.epg_handlers_dict[method] = EPG_Handler(self.fhdhr, plugin, self.id_system)

        print("--------------------------------------------------")
