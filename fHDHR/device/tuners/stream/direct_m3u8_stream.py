import sys
import time
import m3u8
from collections import OrderedDict
from Crypto.Cipher import AES

# from fHDHR.exceptions import TunerError


class Direct_M3U8_Stream():

    def __init__(self, fhdhr, stream_args, tuner):
        self.fhdhr = fhdhr
        self.stream_args = stream_args
        self.tuner = tuner

        self.bytes_per_read = int(self.fhdhr.config.dict["streaming"]["bytes_per_read"])

    def get(self):

        if not self.stream_args["duration"] == 0:
            self.stream_args["time_end"] = self.stream_args["duration"] + time.time()

        self.fhdhr.logger.info("Detected stream of m3u8 URL: %s" % self.stream_args["stream_info"]["url"])

        if self.stream_args["transcode_quality"]:
            self.fhdhr.logger.info("Client requested a %s transcode for stream. Direct Method cannot transcode." % self.stream_args["transcode_quality"])

        segments_dict = OrderedDict()
        start_time = time.time()
        total_secs_served = 0

        def generate():
            total_chunks = 0

            try:

                while self.tuner.tuner_lock.locked():

                    added, removed, played = 0, [], []

                    # (re)Load the m3u8 playlist, apply headers if needbe
                    try:
                        if self.stream_args["stream_info"]["headers"]:
                            playlist = m3u8.load(self.stream_args["stream_info"]["url"], headers=self.stream_args["stream_info"]["headers"])
                        else:
                            playlist = m3u8.load(self.stream_args["stream_info"]["url"])
                    except Exception as e:
                        self.fhdhr.logger.info("Connection Closed: %s" % e)
                        self.tuner.close()
                        return None

                    m3u8_segments = playlist.segments

                    if playlist.keys != [None]:
                        keys = [{"uri": key.absolute_uri, "method": key.method, "iv": key.iv} for key in playlist.keys if key]
                    else:
                        keys = [None for i in range(0, len(m3u8_segments))]

                    # Only add new m3u8_segments to our segments_dict
                    for segment, key in zip(m3u8_segments, keys):
                        uri = segment.absolute_uri
                        if uri not in list(segments_dict.keys()):
                            segments_dict[uri] = {
                                                  "played": False,
                                                  "duration": segment.duration,
                                                  "key": key
                                                  }
                            added += 1
                            self.fhdhr.logger.debug("Adding %s to play queue." % uri)

                            segments_dict[uri]["last_seen"] = time.time()

                    # Cleanup Play Queue
                    for uri, data in list(segments_dict.items()):
                        if data["played"] and (time.time() - data["last_seen"]) > 10:
                            self.fhdhr.logger.debug("Removed %s from play queue." % uri)
                            removed.append(uri)

                    for uri in removed:
                        del segments_dict[uri]

                    self.fhdhr.logger.info("Refreshing m3u8, Loaded %s new segments, removed %s" % (added, len(removed)))

                    for uri, dict in list(segments_dict.items()):

                        if not data["played"]:

                            total_chunks += 1

                            self.fhdhr.logger.debug("Downloading Chunk #%s: %s" % (total_chunks, uri))
                            if self.stream_args["stream_info"]["headers"]:
                                chunk = self.fhdhr.web.session.get(uri, headers=self.stream_args["stream_info"]["headers"]).content
                            else:
                                chunk = self.fhdhr.web.session.get(uri).content

                            if data["key"]:
                                if data["key"]["uri"]:
                                    if self.stream_args["stream_info"]["headers"]:
                                        keyfile = self.fhdhr.web.session.get(data["key"]["uri"], headers=self.stream_args["stream_info"]["headers"]).content
                                    else:
                                        keyfile = self.fhdhr.web.session.get(data["key"]["uri"]).content
                                    cryptor = AES.new(keyfile, AES.MODE_CBC, keyfile)
                                    self.fhdhr.logger.debug("Decrypting Chunk #%s with key: %s" % (total_chunks, data["key"]["uri"]))
                                    chunk = cryptor.decrypt(chunk)

                            played.append(uri)

                            if not chunk:
                                break
                                # raise TunerError("807 - No Video Data")

                            chunk_size = int(sys.getsizeof(chunk))
                            self.fhdhr.logger.info("Passing Through Chunk #%s with size %s" % (total_chunks, chunk_size))
                            yield chunk
                            self.tuner.add_downloaded_size(chunk_size)

                            """
                            if (not self.stream_args["duration"] == 0 and
                               not time.time() < self.stream_args["time_end"]):
                                self.fhdhr.logger.info("Requested Duration Expired.")
                                self.tuner.close()
                            """

                    for uri in played:
                        segments_dict[uri]["played"] = True

                self.fhdhr.logger.info("Connection Closed: Tuner Lock Removed")

            except GeneratorExit:
                self.fhdhr.logger.info("Connection Closed.")
            except Exception as e:
                self.fhdhr.logger.info("Connection Closed: %s" % e)
            finally:
                self.fhdhr.logger.info("Connection Closed: Tuner Lock Removed")
                if hasattr(self.fhdhr.origins.origins_dict[self.tuner.origin], "close_stream"):
                    self.fhdhr.origins.origins_dict[self.tuner.origin].close_stream(self.tuner.number, self.stream_args)
                self.tuner.close()
                # raise TunerError("806 - Tune Failed")

        return generate()
