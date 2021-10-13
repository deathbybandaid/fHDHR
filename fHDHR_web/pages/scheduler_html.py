from flask import request, render_template, session


class Scheduler_HTML():
    endpoints = ["/scheduler", "/scheduler.html"]
    endpoint_name = "page_scheduler_html"
    endpoint_access_level = 2
    pretty_name = "Scheduler"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        return render_template('scheduler.html', request=request, session=session, fhdhr=self.fhdhr)
