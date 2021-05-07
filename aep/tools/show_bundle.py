#!/usr/bin/env python3

"""Pretty print Threat Actor file"""

import argparse
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Text

import tabulate

from aep.tools import config


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("ATT&CK simulator")

    parser.add_argument(
        "-b",
        "--technique-bundle",
        type=Path,
        help="The threat actor file to simulate",
    )

    parser.add_argument('--include-tools', action='store_true',
                        help="Include techniques for threat actor that "
                             "is inherited from tools used")
    parser.add_argument('--no-names', action='store_true',
                        help="Only list technique IDs. This may be usefull on smaller screens.")
    parser.add_argument('--text-length', type=int, default=10,
                        help="Number of char before cutting down texh length in output, "
                             "default=10, min=5")

    args: argparse.Namespace = config.handle_args(parser, "show-bundle")

    if not args.technique_bundle:
        sys.stderr.write("--technique-bundle must be specified\n")
        sys.exit(1)

    if args.text_length < 5:
        args.text_length = 5

    return args


def shorten(data: Text, n: int = 10) -> Text:
    """Shorten a string if it is long and n, adding ellipsis to show shortening"""

    if len(data) <= n:
        return data

    return f"{data[:n - 3]}..."


def format(ID: Text, technique: Dict, n: int = 10, ID_only: bool = False) -> Text:
    """Format a technique ID + name for output. n is the number of charcters
    include from ID and Name"""

    if ID_only:
        return shorten(ID, n)

    return f"{shorten(ID, n)} [{shorten(technique['name'], n)}]"


def main() -> None:
    """main entry"""

    args = command_line_arguments()

    tactics: OrderedDict = OrderedDict()
    tactics["Reconnaissance"] = []
    tactics["Resource Development"] = []
    tactics["Initial Access"] = []
    tactics["Execution"] = []
    tactics["Persistence"] = []
    tactics["Privilege Escalation"] = []
    tactics["Defense Evasion"] = []
    tactics["Credential Access"] = []
    tactics["Discovery"] = []
    tactics["Lateral Movement"] = []
    tactics["Collection"] = []
    tactics["Command and Control"] = []
    tactics["Exfiltration"] = []
    tactics["Impact"] = []

    techniques, tech_bundle = config.read_data(args)

    for tech in tech_bundle:
        tech_dict = techniques[tech]
        for tactic in tech_dict["tactic"]:
            tactics[tactic].append(
                format(tech, tech_dict, args.text_length, args.no_names))

    print(tabulate.tabulate(tactics,
                            headers=tactics.keys(),
                            tablefmt="fancy_grid"))


if __name__ == "__main__":
    main()
