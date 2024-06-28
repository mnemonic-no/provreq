#!/usr/bin/env python3

"""Pretty print Threat Actor file"""

import argparse
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Text

import tabulate

from provreq.tools import config


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("ATT&CK simulator")

    parser.add_argument(
        "-b",
        "--agent-bundle",
        type=Path,
        help="The threat actor file to simulate",
    )

    parser.add_argument(
        "--include-tools",
        action="store_true",
        help="Include agents for threat actor that " "is inherited from tools used",
    )
    parser.add_argument(
        "--no-names",
        action="store_true",
        help="Only list agent IDs. This may be usefull on smaller screens.",
    )
    parser.add_argument(
        "--text-length",
        type=int,
        default=10,
        help="Number of char before cutting down texh length in output, "
        "default=10, min=5",
    )

    args: argparse.Namespace = config.handle_args(parser, "show-bundle")

    if not args.agent_bundle:
        sys.stderr.write("--agent-bundle must be specified\n")
        sys.exit(1)

    if args.text_length < 5:
        args.text_length = 5

    return args


def shorten(data: Text, n: int = 10) -> Text:
    """Shorten a string if it is long and n, adding ellipsis to show shortening"""

    if len(data) <= n:
        return data

    return f"{data[:n - 3]}..."


def format(ID: Text, agent: Dict, n: int = 10, ID_only: bool = False) -> Text:
    """Format a agent ID + name for output. n is the number of charcters
    include from ID and Name"""

    if ID_only:
        return shorten(ID, n)

    return f"{shorten(ID, n)} [{shorten(agent['name'], n)}]"


def main() -> None:
    """main entry"""

    args = command_line_arguments()

    agent_classes: OrderedDict = OrderedDict()
    agent_classes["Reconnaissance"] = []
    agent_classes["Resource Development"] = []
    agent_classes["Initial Access"] = []
    agent_classes["Execution"] = []
    agent_classes["Persistence"] = []
    agent_classes["Privilege Escalation"] = []
    agent_classes["Defense Evasion"] = []
    agent_classes["Credential Access"] = []
    agent_classes["Discovery"] = []
    agent_classes["Lateral Movement"] = []
    agent_classes["Collection"] = []
    agent_classes["Command and Control"] = []
    agent_classes["Exfiltration"] = []
    agent_classes["Impact"] = []

    agents, agent_bundle = config.read_data(args)

    for agent in agent_bundle:
        agent_dict = agents[agent]
        for agent_class in agent_dict["agent_class"]:
            agent_classes[agent_class].append(
                format(agent, agent_dict, args.text_length, args.no_names)
            )

    print(tabulate.tabulate(agent_classes, headers=agent_classes.keys(), tablefmt="fancy_grid"))


if __name__ == "__main__":
    main()
