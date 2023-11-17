from urllib.parse import urlparse, urlunparse

import requests
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
    def bit_rate(self):
        return self.raw.get("bitrate")

    @property
    def media_type(self):
        return self.raw.get("media_type")

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

    @property
    def dict(self):
        """Return a dict representation of the station."""
        return {
            "artist": self.artist,
            "bit_rate": self.bit_rate,
            "description": self.description,
            "image": self.image,
            "match": self.match(),
            "media_type": self.media_type,
            "stream": self.stream,
            "title": self.title,
        }


class TuneIn:
    search_url = "https://opml.radiotime.com/Search.ashx"
    featured_url = "http://opml.radiotime.com/Browse.ashx?c=local"  # local stations

    @staticmethod
    def get_stream_urls(url):
        _url = urlparse(url)
        for scheme in ("http", "https"):
            url_str = urlunparse(
                _url._replace(scheme=scheme, query=_url.query + "&render=json")
            )
            res = requests.get(url_str)
            try:
                res.raise_for_status()
                break
            except requests.exceptions.RequestException:
                continue
        else:
            return "Failed to get stream url"

        return res.json().get("body", {})

    @staticmethod
    def featured():
        res = requests.post(TuneIn.featured_url)
        return list(TuneIn._get_stations(res))

    @staticmethod
    def search(query):
        res = requests.post(
            TuneIn.search_url,
            data={"query": query, "formats": "mp3,aac,ogg,html,hls", "render": "json"},
        )
        return list(TuneIn._get_stations(res, query))

    @staticmethod
    def _get_stations(res: requests.Response, query: str = ""):
        stations = res.json().get("body", [])

        for entry in stations:
            if (
                entry.get("key") == "unavailable"
                or entry.get("type") != "audio"
                or entry.get("item") != "station"
            ):
                continue
            streams = TuneIn.get_stream_urls(entry["URL"])
            for stream in streams:
                yield TuneInStation(
                    {
                        "stream": stream["url"],
                        "bitrate": stream["bitrate"],
                        "media_type": stream["media_type"],
                        "url": entry["URL"],
                        "title": entry.get("current_track") or entry.get("text"),
                        "artist": entry.get("text"),
                        "description": entry.get("subtext"),
                        "image": entry.get("image"),
                        "query": query,
                    }
                )
