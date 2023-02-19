import requests
from tunein.xml_helper import xml2dict
from tunein.parse import fuzzy_match


class TuneInStation:
    def __init__(self, raw):
        self.raw = raw

    @property
    def title(self):
        return self.raw.get("title", "")
    
    @property
    def artist(self):
        return self.raw.get("artist", "")

    @property
    def image(self):
        return self.raw.get("image")

    @property
    def description(self):
        return self.raw.get("description", "")

    @property
    def stream(self):
        return self.raw.get("stream")

    def match(self, phrase=None):
        phrase = phrase or self.raw.get("query")
        if not phrase:
            return 0
        return fuzzy_match(phrase.lower(), self.title.lower()) * 100

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title


class TuneIn:
    search_url = "http://opml.radiotime.com/Search.ashx"
    featured_url = "http://opml.radiotime.com/Browse.ashx?c=local"  # local stations

    @staticmethod
    def get_stream_url(url):
        res = requests.get(url)
        for url in res.text.splitlines():
            if (len(url) > 4):
                if url[-3:] == 'm3u':
                    return url[:-4]
                if url[-3:] == 'pls':
                    res2 = requests.get(url)
                    # Loop through the data looking for the first url
                    for line in res2.text.splitlines():
                        if line.startswith("File1="):
                            return line[6:]
                else:
                    return url

    @staticmethod
    def featured():
        res = requests.post(TuneIn.featured_url)
        yield from TuneIn._get_stations(res)

    @staticmethod
    def search(query):
        res = requests.post(TuneIn.search_url, data={"query": query})
        yield from TuneIn._get_stations(res, query)

    @staticmethod
    def _get_stations(res: requests.Response, query: str = ""):
        res = xml2dict(res.text)
        if not res.get("opml"):
            return
        # stations might be nested based on Playlist/Search
        outline = res['opml']['body']["outline"]

        if isinstance(outline, list):
            outline = outline[0]
        assert isinstance(outline, dict)
        if outline.get("outline"):
            stations = outline["outline"]
        else:
            stations = outline
        for entry in stations:
            try:
                if not entry.get("key") == "unavailable" \
                        and entry.get("type") == "audio" \
                        and entry.get("item") == "station":
                    yield TuneInStation(
                        {"stream": TuneIn.get_stream_url(entry["URL"]),
                         "url": entry["URL"],
                         "title": entry.get("current_track") or entry.get("text"),
                         "artist": entry.get("text"),
                         "description": entry.get("subtext"),
                         "image": entry.get("image"),
                         "query": query
                         })
            except:
                continue
