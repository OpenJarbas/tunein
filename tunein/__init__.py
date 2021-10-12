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
    def search(query):
        res = requests.post(TuneIn.search_url, data={"query": query})
        for entry in xml2dict(res.text)['opml']['body']["outline"]:
            if entry.get("type") == "audio" and entry.get("item") == "station":
                yield TuneInStation(
                    {"stream": TuneIn.get_stream_url(entry["URL"]),
                     "url": entry["URL"],
                     "title": entry.get("current_track") or entry.get("text"),
                     "artist": entry.get("text"),
                     "description": entry.get("subtext"),
                     "image": entry.get("image"),
                     "query": query
                     })

