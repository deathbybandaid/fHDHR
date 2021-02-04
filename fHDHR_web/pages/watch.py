from flask import request, render_template, session


class Watch_HTML():
    endpoints = ["/watch", "/watch.html"]
    endpoint_name = "page_watch_html"
    endpoint_access_level = 0
    pretty_name = "Watch"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        base_url = request.url_root[:-1]

        origin = self.fhdhr.origins.valid_origins[0]
        channel_id = [x["id"] for x in self.fhdhr.device.channels.get_channels(origin)][0]

        watch_url = '%s/api/tuners?method=watch&channel=%s&origin=%s' % (base_url, channel_id, origin)

        return render_template('watch.html', request=request, session=session, fhdhr=self.fhdhr, watch_url=watch_url)
