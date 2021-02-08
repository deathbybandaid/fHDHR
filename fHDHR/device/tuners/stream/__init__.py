import m3u8


from .direct_stream import Direct_Stream
from .direct_m3u8_stream import Direct_M3U8_Stream
from fHDHR.exceptions import TunerError


class Stream():

    def __init__(self, fhdhr, channels, tuner, stream_args):
        self.fhdhr = fhdhr
        self.channels = channels
        self.tuner = tuner
        self.stream_args = stream_args
        self.clients = []
        self.get_stream_info()

    def add_client(self, client_info):
        if client_info["id"] not in [x["id"] for x in self.clients]:
            self.clients.append(client_info)

    def del_client(self, client_info):
        if client_info["id"] in [x["id"] for x in self.clients]:
            self.clients = [x for x in self.clients if x["id"] != client_info["id"]]

    def get(self):
        return self.method.get()

    def get_stream_info(self):

        self.stream_info = self.channels.get_channel_stream(self.stream_args, self.stream_args["origin"])
        if not self.stream_info:
            raise TunerError("806 - Tune Failed")

        if isinstance(self.stream_info, str):
            self.stream_info = {"url": self.stream_info, "headers": None}
        self.stream_args["stream_info"] = self.stream_info

        if not self.stream_args["stream_info"]["url"]:
            raise TunerError("806 - Tune Failed")

        if "headers" not in list(self.stream_args["stream_info"].keys()):
            self.stream_args["stream_info"]["headers"] = None

        if self.stream_args["stream_info"]["url"].startswith("udp://"):
            self.stream_args["true_content_type"] = "video/mpeg"
            self.stream_args["content_type"] = "video/mpeg"
        else:

            channel_stream_url_headers = self.fhdhr.web.session.head(self.stream_args["stream_info"]["url"]).headers
            self.stream_args["true_content_type"] = channel_stream_url_headers['Content-Type']

            if self.stream_args["true_content_type"].startswith(tuple(["application/", "text/"])):
                self.stream_args["content_type"] = "video/mpeg"
                if self.stream_args["origin_quality"] != -1:
                    self.stream_args["stream_info"]["url"] = self.m3u8_quality(self.stream_args)
            else:
                self.stream_args["content_type"] = self.stream_args["true_content_type"]

        if self.stream_args["method"] == "direct":
            if self.stream_args["true_content_type"].startswith(tuple(["application/", "text/"])):
                self.method = Direct_M3U8_Stream(self.fhdhr, self.stream_args, self.tuner)
            else:
                self.method = Direct_Stream(self.fhdhr, self.stream_args, self.tuner)
        else:
            plugin_name = self.fhdhr.config.dict["streaming"]["valid_methods"][self.stream_args["method"]]["plugin"]
            self.method = self.fhdhr.plugins.plugins[plugin_name].Plugin_OBJ(self.fhdhr, self.fhdhr.plugins.plugins[plugin_name].plugin_utils, self.stream_args, self.tuner)

    def m3u8_quality(self, stream_args):

        m3u8_url = stream_args["stream_info"]["url"]
        quality_profile = stream_args["origin_quality"]

        if not quality_profile:
            if stream_args["method"] == "direct":
                quality_profile = "high"
                self.fhdhr.logger.info("Origin Quality not set in config. Direct Method set and will default to Highest Quality")
            else:
                self.fhdhr.logger.info("Origin Quality not set in config. %s Method will select the Quality Automatically" % stream_args["method"])
                return m3u8_url
        else:
            quality_profile = quality_profile.lower()
            self.fhdhr.logger.info("Origin Quality set in config to %s" % (quality_profile))

        while True:
            self.fhdhr.logger.info("Opening m3u8 for reading %s" % m3u8_url)

            try:
                if stream_args["stream_info"]["headers"]:
                    videoUrlM3u = m3u8.load(m3u8_url, headers=stream_args["stream_info"]["headers"])
                else:
                    videoUrlM3u = m3u8.load(m3u8_url)
            except Exception as e:
                self.fhdhr.logger.info("m3u8 load error: %s" % e)
                return m3u8_url

            if len(videoUrlM3u.playlists):
                self.fhdhr.logger.info("%s m3u8 varients found" % len(videoUrlM3u.playlists))

                # Create list of dicts
                playlists, playlist_index = {}, 0
                for playlist_item in videoUrlM3u.playlists:
                    playlist_index += 1
                    playlist_dict = {
                                    "url": playlist_item.absolute_uri,
                                    "bandwidth": playlist_item.stream_info.bandwidth,
                                    }

                    if not playlist_item.stream_info.resolution:
                        playlist_dict["width"] = None
                        playlist_dict["height"] = None
                    else:
                        try:
                            playlist_dict["width"] = playlist_item.stream_info.resolution[0]
                            playlist_dict["height"] = playlist_item.stream_info.resolution[1]
                        except TypeError:
                            playlist_dict["width"] = None
                            playlist_dict["height"] = None

                    playlists[playlist_index] = playlist_dict

                sorted_playlists = sorted(playlists, key=lambda i: (
                    int(playlists[i]['bandwidth']),
                    int(playlists[i]['width'] or 0),
                    int(playlists[i]['height'] or 0)
                    ))
                sorted_playlists = [playlists[x] for x in sorted_playlists]

                if not quality_profile or quality_profile == "high":
                    selected_index = -1
                elif quality_profile == "medium":
                    selected_index = int((len(sorted_playlists) - 1)/2)
                elif quality_profile == "low":
                    selected_index = 0

                m3u8_stats = ",".join(
                    ["%s %s" % (x, sorted_playlists[selected_index][x])
                     for x in list(sorted_playlists[selected_index].keys())
                     if x != "url" and sorted_playlists[selected_index][x]])
                self.fhdhr.logger.info("Selected m3u8 details: %s" % m3u8_stats)
                m3u8_url = sorted_playlists[selected_index]["url"]

            else:
                self.fhdhr.logger.info("No m3u8 varients found")
                break

        return m3u8_url
