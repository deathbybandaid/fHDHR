import sys
import time
import socket
import re

from fHDHR.exceptions import TunerError


class Direct_RTP_Stream():

    def __init__(self, fhdhr, stream_args, tuner):
        self.fhdhr = fhdhr
        self.stream_args = stream_args
        self.tuner = tuner

        self.bytes_per_read = int(self.fhdhr.config.dict["streaming"]["bytes_per_read"])

        self.fhdhr.logger.info("Attempting to create socket to listen on.")
        self.address = self.get_sock_address()
        if not self.address:
            raise TunerError("806 - Tune Failed: Could Not Create Socket")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, 0))

        self.fhdhr.logger.info("Create socket at %s:%s." % (self.socket.getsockname()[0], self.socket.getsockname()[1]))

        self.socket.close()

    def get_sock_address(self):
        if self.fhdhr.config.dict["fhdhr"]["discovery_address"]:
            return self.fhdhr.config.dict["fhdhr"]["discovery_address"]
        else:
            try:
                base_url = self.stream_args["base_url"].split("://")[1].split(":")[0]
            except IndexError:
                return None
            ip_match = re.match('^' + '[\.]'.join(['(\d{1,3})']*4) + '$', base_url)
            ip_validate = bool(ip_match)
            if ip_validate:
                return base_url
        return None

    def get(self):

        if not self.stream_args["duration"] == 0:
            self.stream_args["time_end"] = self.stream_args["duration"] + time.time()

        self.fhdhr.logger.info("Direct Stream of %s URL: %s" % (self.stream_args["true_content_type"], self.stream_args["stream_info"]["url"]))

        if self.stream_args["transcode_quality"]:
            self.fhdhr.logger.info("Client requested a %s transcode for stream. Direct Method cannot transcode." % self.stream_args["transcode_quality"])

        if self.stream_args["stream_info"]["headers"]:
            req = self.fhdhr.web.session.get(self.stream_args["stream_info"]["url"], stream=True, headers=self.stream_args["stream_info"]["headers"])
        else:
            req = self.fhdhr.web.session.get(self.stream_args["stream_info"]["url"], stream=True)

        def generate():

            try:

                chunk_counter = 1

                while self.tuner.tuner_lock.locked():

                    for chunk in req.iter_content(chunk_size=self.bytes_per_read):

                        if (not self.stream_args["duration"] == 0 and
                           not time.time() < self.stream_args["time_end"]):
                            req.close()
                            self.fhdhr.logger.info("Requested Duration Expired.")
                            self.tuner.close()

                        if not chunk:
                            break
                            # raise TunerError("807 - No Video Data")

                        chunk_size = int(sys.getsizeof(chunk))
                        self.fhdhr.logger.info("Passing Through Chunk #%s with size %s" % (chunk_counter, chunk_size))
                        yield chunk
                        self.tuner.add_downloaded_size(chunk_size)

                        chunk_counter += 1

                self.fhdhr.logger.info("Connection Closed: Tuner Lock Removed")

            except GeneratorExit:
                self.fhdhr.logger.info("Connection Closed.")
            except Exception as e:
                self.fhdhr.logger.info("Connection Closed: %s" % e)
            finally:
                req.close()
                self.fhdhr.logger.info("Connection Closed: Tuner Lock Removed")
                if hasattr(self.fhdhr.origins.origins_dict[self.tuner.origin], "close_stream"):
                    self.fhdhr.origins.origins_dict[self.tuner.origin].close_stream(self.tuner.number, self.stream_args)
                self.tuner.close()
                # raise TunerError("806 - Tune Failed")

        return generate()
