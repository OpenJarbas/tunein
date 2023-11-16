"""The CLI entrypoint for tunein."""

import argparse

from tunein import subcommands

class Cli:
    """The CLI entrypoint for tunein."""

    def __init__(self) -> None:
        """Initialize the CLI entrypoint."""
        self._args: argparse.Namespace
    
    def parse_args(self) -> None:
        """Parse the command line arguments."""
        parser = argparse.ArgumentParser(
            description="unnoficial python api for TuneIn.",
        )

        subparsers = parser.add_subparsers(
            title="Commands",
            dest="subcommand",
            metavar="",
            required=True,
        )

        search = subparsers.add_parser(
            "search",
            help="Search tunein for stations",
        )

        search.add_argument(
            "station",
            help="Station to search for",
        )

        search.add_argument(
            "-f", "--format",
            choices=["json", "table"],
            default="table",
            help="Output format",
        )
    
        self._args = parser.parse_args()

    def run(self) -> None:
        """Run the CLI."""
        subcommand_cls = getattr(subcommands, self._args.subcommand.capitalize())
        subcommand = subcommand_cls(args=self._args)
        subcommand.run()

def main() -> None:
    """Run the CLI."""
    cli = Cli()
    cli.parse_args()
    cli.run()
  

if __name__ == "__main__":
    main()



