import threading
import datetime
import time

from fHDHR.exceptions import TunerError
from fHDHR.tools import humanized_time

from .stream import Stream


class Tuner():
    def __init__(self, fhdhr, inum, epg, origin):
        self.fhdhr = fhdhr

        self.number = inum
        self.origin = origin
        self.epg = epg

        self.tuner_lock = threading.Lock()
        self.current_stream = None
        self.current_stream_content = []
        self.status = {"status": "Inactive"}

        self.chanscan_url = "/api/channels?method=scan"
        self.close_url = "/api/tuners?method=close&tuner=%s&origin=%s" % (self.number, self.origin)
        self.start_url = "/api/tuners?method=start&tuner=%s&origin=%s" % (self.number, self.origin)

    def channel_scan(self, origin, grabbed=False):
        if self.tuner_lock.locked() and not grabbed:
            self.fhdhr.logger.error("%s Tuner #%s is not available." % (self.origin, self.number))
            raise TunerError("804 - Tuner In Use")

        if self.status["status"] == "Scanning":
            self.fhdhr.logger.info("Channel Scan Already In Progress!")
        else:

            if not grabbed:
                self.tuner_lock.acquire()
            self.status["status"] = "Scanning"
            self.status["origin"] = origin
            self.status["time_start"] = datetime.datetime.utcnow()
            self.fhdhr.logger.info("Tuner #%s Performing Channel Scan for %s origin." % (self.number, origin))

            chanscan = threading.Thread(target=self.runscan, args=(origin,))
            chanscan.start()

    def runscan(self, origin):
        self.fhdhr.api.get("%s&origin=%s" % (self.chanscan_url, origin))
        self.fhdhr.logger.info("Requested Channel Scan for %s origin Complete." % origin)
        self.close()
        self.fhdhr.api.get(self.close_url)

    def add_downloaded_size(self, bytes_count):
        if "downloaded" in list(self.status.keys()):
            self.status["downloaded"] += bytes_count

    def grab(self, origin, channel_number):
        if self.tuner_lock.locked():
            self.fhdhr.logger.error("Tuner #%s is not available." % self.number)
            raise TunerError("804 - Tuner In Use")
        self.tuner_lock.acquire()
        self.status["status"] = "Acquired"
        self.status["origin"] = origin
        self.status["channel"] = channel_number
        self.status["time_start"] = datetime.datetime.utcnow()
        self.fhdhr.logger.info("Tuner #%s Acquired." % str(self.number))

    def close(self, force=False):
        self.set_off_status()
        if self.tuner_lock.locked():
            self.tuner_lock.release()
            self.fhdhr.logger.info("Tuner #%s Released." % self.number)

    def get_status(self):
        current_status = self.status.copy()
        current_status["epg"] = {}
        if current_status["status"] in ["Acquired", "Active", "Scanning"]:
            current_status["running_time"] = str(
                humanized_time(
                    int((datetime.datetime.utcnow() - current_status["time_start"]).total_seconds())))
            current_status["time_start"] = str(current_status["time_start"])
        if current_status["status"] in ["Active"]:
            if current_status["origin"] in self.epg.epg_methods:
                current_status["epg"] = self.epg.whats_on_now(current_status["channel"], method=current_status["origin"])
        return current_status

    def set_off_status(self):
        self.current_stream = None
        self.current_stream_content = []
        self.status = {"status": "Inactive"}

    def tune(self):
        while self.tuner_lock.locked():
            for chunk in self.current_stream.get():
                self.current_stream_content.append(chunk)
                if len(self.current_stream_content) > 3:
                    self.current_stream_content = self.current_stream_content[-3:]
        self.close()

    def get_stream(self):
        time.sleep(2)

        def generate():
            try:
                while True:
                    if not len(self.current_stream_content):
                        break
                    chunk = self.current_stream_content[-1]
                    yield chunk
            except GeneratorExit:
                self.fhdhr.logger.info("Connection Closed.")
            except Exception as e:
                self.fhdhr.logger.info("Connection Closed: %s" % e)
            finally:
                self.fhdhr.logger.info("Connection Closed: Tuner Lock Removed")

        return generate()

    def setup_stream(self, stream_args, tuner):
        self.current_stream = Stream(self.fhdhr, stream_args, tuner)

    def set_status(self, stream_args):
        if self.status["status"] != "Active":
            self.status = {
                            "status": "Active",
                            "clients": stream_args["clients"],
                            "method": stream_args["method"],
                            "origin": stream_args["origin"],
                            "channel": stream_args["channel"],
                            "proxied_url": stream_args["stream_info"]["url"],
                            "time_start": datetime.datetime.utcnow(),
                            "downloaded": 0
                            }
        else:
            for client in stream_args["clients"]:
                if client["client_id"] not in [x["client_id"] for x in self.status["clients"]]:
                    self.status["clients"].extend(stream_args["clients"])
