from flask import request, redirect
import urllib.parse


class Scheduler_API():
    endpoints = ["/api/scheduler"]
    endpoint_name = "api_scheduler"
    endpoint_methods = ["GET", "POST"]
    endpoint_default_parameters = {
                                    "method": "get"
                                    }

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        redirect_url = request.args.get('redirect', default=None, type=str)
        method = "Test"

        if redirect_url:
            if "?" in redirect_url:
                return redirect("%s&retmessage=%s" % (redirect_url, urllib.parse.quote("%s Success" % method)))
            else:
                return redirect("%s?retmessage=%s" % (redirect_url, urllib.parse.quote("%s Success" % method)))
        else:
            if method == "scan":
                return redirect('/lineup_status.json')
            else:
                return "%s Success" % method
