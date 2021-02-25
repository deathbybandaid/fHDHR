

class Plugin_OBJ():

    def __init__(self, plugin_utils):
        self.plugin_utils = plugin_utils

        self.proto = "rtp://" if self.plugin_utils.config.dict['rtpcamera']["ssl"] else "rtsp://"
        self.address = self.plugin_utils.config.dict["rtpcamera"]["address"]
        self.port = self.plugin_utils.config.dict["rtpcamera"]["port"]
        self.username = self.plugin_utils.config.dict["rtpcamera"]["username"]
        self.password = self.plugin_utils.config.dict["rtpcamera"]["password"]

    def get_channels(self):
        return [{"id": "test"}]

    def get_channel_stream(self, chandict, stream_args):
        streamurl = ('%s%s:%s@%s:%s' %
                     (self.proto,
                      self.username,
                      self.password,
                      self.address,
                      self.port))
        stream_info = {"url": streamurl}
        return stream_info
