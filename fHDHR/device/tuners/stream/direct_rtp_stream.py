import socket
import re

from fHDHR.exceptions import TunerError


class Direct_Stream():

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

    def get(self):

        self.fhdhr.logger.info("Direct Stream of %s URL: %s" % (self.stream_args["true_content_type"], self.stream_args["stream_info"]["url"]))

        if self.stream_args["transcode_quality"]:
            self.fhdhr.logger.info("Client requested a %s transcode for stream. Direct Method cannot transcode." % self.stream_args["transcode_quality"])

        self.socket.send("GET", self.stream_args["stream_info"]["url"])

        def generate():

            chunk_counter = 0

            try:

                while self.tuner.tuner_lock.locked():

                    chunk = self.socket.recv(self.bytes_per_read)
                    chunk_counter += 1
                    self.fhdhr.logger.debug("Downloading Chunk #%s" % chunk_counter)

                    if not chunk:
                        break

                    yield chunk

            finally:
                self.socket.close()

        return generate()

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
