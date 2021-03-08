from flask import request, redirect, Response
import urllib.parse
from io import StringIO


class Logs():
    endpoints = ["/api/logs"]
    endpoint_name = "api_logs"
    endpoint_methods = ["GET", "POST"]

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        method = request.args.get('method', default="text", type=str)
        redirect_url = request.args.get('redirect', default=None, type=str)

        if method == "text":

            fakefile = StringIO()

            for log_entry in list(self.fhdhr.logger.memory.dict.keys()):
                fakefile.write("%s\n" % self.fhdhr.logger.memory.dict[log_entry]["fmsg"])

            logfile = fakefile.getvalue()

            return Response(status=200, response=logfile, mimetype='text/plain')

        if redirect_url:
            if "?" in redirect_url:
                return redirect("%s&retmessage=%s" % (redirect_url, urllib.parse.quote("%s Success" % method)))
            else:
                return redirect("%s?retmessage=%s" % (redirect_url, urllib.parse.quote("%s Success" % method)))
        else:
            return "%s Success" % method
