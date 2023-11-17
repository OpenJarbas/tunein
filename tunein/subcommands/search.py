"""The search subcommand for tunein."""

from __future__ import annotations

import argparse
import json
import shutil
import sys

from tunein import TuneIn


class Ansi:
    """ANSI escape codes."""

    BLUE = "\x1B[34m"
    BOLD = "\x1B[1m"
    CYAN = "\x1B[36m"
    GREEN = "\x1B[32m"
    ITALIC = "\x1B[3m"
    MAGENTA = "\x1B[35m"
    RED = "\x1B[31m"
    RESET = "\x1B[0m"
    REVERSED = "\x1B[7m"
    UNDERLINE = "\x1B[4m"
    WHITE = "\x1B[37m"
    YELLOW = "\x1B[33m"
    GREY = "\x1B[90m"


NOPRINT_TRANS_TABLE = {
    i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable()
}


class Search:
    """The search subcommand for tunein."""

    def __init__(self: Search, args: argparse.Namespace) -> None:
        """Initialize the search subcommand."""
        self._args: argparse.Namespace = args

    def run(self: Search) -> None:
        """Run the search subcommand."""
        tunein = TuneIn()
        results = tunein.search(self._args.station)
        stations = [station.dict for station in results]
        if not stations:
            print(f"No results for {self._args.station}")
            sys.exit(1)
        stations.sort(key=lambda x: (x["match"], x["bit_rate"]), reverse=True)
        for station in stations:
            station["title"] = self._printable(station["title"])
            station["artist"] = self._printable(station["artist"])
            station["description"] = self._printable(station["description"])

        if self._args.format == "json":
            print(json.dumps(stations, indent=4))
        elif self._args.format == "table":
            max_widths = {}
            columns = ["title", "bit_rate", "media_type", "artist", "description"]
            for column in columns:
                max_width = max(
                    [len(str(station[column])) for station in stations] + [len(column)]
                )
                if column == "description":
                    term_width = shutil.get_terminal_size().columns
                    remaining = (
                        term_width
                        - sum(
                            [
                                max_widths[column]
                                for column in columns
                                if column != "description"
                            ]
                        )
                        - len(columns)
                        - 1
                    )
                    max_width = min(max_width, remaining)
                max_widths[column] = max_width

            print(
                " ".join(
                    column.ljust(max_widths[column]).capitalize().replace("_", " ")
                    for column in columns
                )
            )
            print(" ".join("-" * max_widths[column] for column in columns))
            for station in stations:
                line_parts = []
                # title as link
                link = self._term_link(station.get("stream"), station["title"])
                line_parts.append(
                    f"{link}{' '*(max_widths['title']-len(station['title']))}"
                )
                # bit rate
                line_parts.append(
                    str(station["bit_rate"]).ljust(max_widths["bit_rate"])
                )
                # media type
                line_parts.append(
                    str(station["media_type"]).ljust(max_widths["media_type"])
                )
                # artist
                line_parts.append(str(station["artist"]).ljust(max_widths["artist"]))
                # description clipped
                line_parts.append(
                    str(station["description"])[: max_widths["description"]]
                )
                print(" ".join(line_parts))

    @staticmethod
    def _term_link(uri: str, label: str) -> str:
        """Return a link.

        Args:
            uri: The URI to link to
            label: The label to use for the link
        Returns:
            The link
        """
        parameters = ""

        # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
        escape_mask = "\x1b]8;{};{}\x1b\\{}\x1b]8;;\x1b\\"
        link_str = escape_mask.format(parameters, uri, label)
        return f"{Ansi.BLUE}{link_str}{Ansi.RESET}"

    @staticmethod
    def _printable(string: str) -> str:
        """Replace non-printable characters in a string.

        Args:
            string: The string to replace non-printable characters in.
        Returns:
            The string with non-printable characters replaced.
        """
        return string.translate(NOPRINT_TRANS_TABLE)
