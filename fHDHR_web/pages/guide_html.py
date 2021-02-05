from flask import request, session, render_template
import datetime

from fHDHR.tools import channel_sort, humanized_time


class Guide_HTML():
    endpoints = ["/guide", "/guide.html"]
    endpoint_name = "page_guide_html"
    endpoint_access_level = 0
    pretty_name = "Guide"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        nowtime = datetime.datetime.utcnow().timestamp()

        source = request.args.get('source', default=self.fhdhr.device.epg.def_method, type=str)
        epg_methods = self.fhdhr.device.epg.valid_epg_methods
        if source not in epg_methods:
            source = self.fhdhr.device.epg.def_method

        origin_methods = self.fhdhr.origins.valid_origins

        channelslist = {}
        unmatched_origins = {}

        if not source:
            return render_template('guide.html', request=request, session=session, fhdhr=self.fhdhr, channelslist=channelslist, epg_methods=epg_methods, origin=source, origin_methods=origin_methods, list=list)

        whatson_all = self.fhdhr.device.epg.whats_on_allchans(source)

        sorted_channel_list = channel_sort([x for x in list(whatson_all.keys())])

        for origin in origin_methods:
            unmatched_origins[origin] = self.fhdhr.device.epg.get_epg_chan_unmatched(origin, source)

        for channel in sorted_channel_list:
            channel_dict, channel_number = self.create_channeldict(source, origin_methods, epg_methods, whatson_all, nowtime, channel)

            channelslist[channel_number] = channel_dict

        return render_template('guide.html', request=request, session=session, fhdhr=self.fhdhr, channelslist=channelslist, epg_methods=epg_methods, origin=source, origin_methods=origin_methods, unmatched_origins=unmatched_origins, list=list)

    def create_channeldict(self, source, origin_methods, epg_methods, whatson_all, nowtime, channel):
        now_playing = whatson_all[channel]["listing"][0]

        if source in origin_methods:
            print(whatson_all[channel]["id"])
            channel_obj = self.fhdhr.device.channels.get_channel_obj("origin_id", whatson_all[channel]["id"], source)
            if channel_obj:

                channel_dict = {
                                "id": channel_obj.dict["id"],
                                "name": channel_obj.dict["name"],
                                "number": channel_obj.number,
                                "chan_thumbnail": channel_obj.thumbnail,
                                "m3u_url": channel_obj.api_m3u_url,
                                "listing_title": now_playing["title"],
                                "listing_thumbnail": now_playing["thumbnail"],
                                "listing_description": now_playing["description"],
                                }

                if now_playing["time_end"]:
                    channel_dict["listing_remaining_time"] = humanized_time(now_playing["time_end"] - nowtime)
                else:
                    channel_dict["listing_remaining_time"] = "N/A"

                for time_item in ["time_start", "time_end"]:

                    if not now_playing[time_item]:
                        channel_dict["listing_%s" % time_item] = "N/A"
                    elif str(now_playing[time_item]).endswith(tuple(["+0000", "+00:00"])):
                        channel_dict["listing_%s" % time_item] = str(now_playing[time_item])
                    else:
                        channel_dict["listing_%s" % time_item] = str(datetime.datetime.fromtimestamp(now_playing[time_item]))

                return channel_dict, channel_obj.number

        channel_dict = {
                        "id": whatson_all[channel]["id"],
                        "name": whatson_all[channel]["name"],
                        "number": whatson_all[channel]["number"],
                        "chan_thumbnail": whatson_all[channel]["thumbnail"],
                        "m3u_url": None,
                        "listing_title": now_playing["title"],
                        "listing_thumbnail": now_playing["thumbnail"],
                        "listing_description": now_playing["description"],
                        }

        if now_playing["time_end"]:
            channel_dict["listing_remaining_time"] = humanized_time(now_playing["time_end"] - nowtime)
        else:
            channel_dict["listing_remaining_time"] = "N/A"

        for time_item in ["time_start", "time_end"]:

            if not now_playing[time_item]:
                channel_dict["listing_%s" % time_item] = "N/A"
            elif str(now_playing[time_item]).endswith(tuple(["+0000", "+00:00"])):
                channel_dict["listing_%s" % time_item] = str(now_playing[time_item])
            else:
                channel_dict["listing_%s" % time_item] = str(datetime.datetime.fromtimestamp(now_playing[time_item]))

        if source in epg_methods:
            channel_dict["chan_match"] = self.fhdhr.device.epg.get_epg_chan_match(source, whatson_all[channel]["id"])
            if channel_dict["chan_match"]:
                chan_obj = self.fhdhr.device.channels.get_channel_obj("id", channel_dict["chan_match"]["fhdhr_id"], channel_dict["chan_match"]["origin"])
                channel_dict["chan_match"]["number"] = chan_obj.number
                channel_dict["chan_match"]["name"] = chan_obj.dict["name"]

        return channel_dict, channel
