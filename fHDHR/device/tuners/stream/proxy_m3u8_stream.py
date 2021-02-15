import time
import datetime
import m3u8
from io import StringIO


class Proxy_M3U8_Stream():

    def __init__(self, fhdhr, stream_args, tuner):
        self.fhdhr = fhdhr
        self.stream_args = stream_args
        self.tuner = tuner

        self.m3u8_file = StringIO()
        self.last_requested = datetime.datetime.utcnow()

    def update_request_time(self):
        self.last_requested = datetime.datetime.utcnow()
        print(self.last_requested)

    def get(self):

        self.fhdhr.logger.info("Proxying stream of m3u8 URL: %s" % self.stream_args["stream_info"]["url"])

        if self.stream_args["transcode_quality"]:
            self.fhdhr.logger.info("Client requested a %s transcode for stream. Proxy_M3U8 Method cannot transcode." % self.stream_args["transcode_quality"])

        try:
            start_time = datetime.datetime.utcnow()
            total_secs_served = 0

            while self.tuner.tuner_lock.locked():

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

                self.fhdhr.logger.info("Updating m3u8 file.")
                self.m3u8_file = StringIO(playlist.dumps())

                for line in playlist.dumps().readlines():
                    print(line)

                duration = sum([segment.duration for segment in playlist.segments])

                runtime = (datetime.datetime.utcnow() - start_time).total_seconds()
                target_diff = 0.5 * duration

                if total_secs_served > 0:
                    wait = total_secs_served - target_diff - runtime
                else:
                    wait = 0

                total_secs_served += duration

                # We can't wait negative time..
                if wait > 0:
                    time.sleep(wait)

                if self.stream_args["duration"]:
                    if (total_secs_served >= int(self.stream_args["duration"])) or (runtime >= self.stream_args["duration"]):
                        self.fhdhr.logger.info("Requested Duration Expired.")
                        self.tuner.close()

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
