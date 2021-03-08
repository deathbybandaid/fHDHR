
from .root_url import Root_URL
from .startup_tasks import Startup_Tasks

from .settings import Settings
from .logs import Logs
from .versions import Versions
from .channels import Channels
from .origins import Origins
from .xmltv import xmlTV
from .m3u import M3U
from .w3u import W3U
from .epg import EPG
from .tuners import Tuners
from .debug import Debug_JSON
from .plugins import Plugins
from .ssdp import SSDP_API

from .route_list import Route_List

from .images import Images


class fHDHR_API():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.root_url = Root_URL(fhdhr)
        self.startup_tasks = Startup_Tasks(fhdhr)

        self.settings = Settings(fhdhr)
        self.logs = Logs(fhdhr)
        self.versions = Versions(fhdhr)
        self.channels = Channels(fhdhr)
        self.origins = Origins(fhdhr)
        self.xmltv = xmlTV(fhdhr)
        self.m3u = M3U(fhdhr)
        self.w3u = W3U(fhdhr)
        self.epg = EPG(fhdhr)
        self.tuners = Tuners(fhdhr)
        self.debug = Debug_JSON(fhdhr)
        self.plugins = Plugins(fhdhr)
        self.ssdp = SSDP_API(fhdhr)

        self.route_list = Route_List(fhdhr)

        self.images = Images(fhdhr)
