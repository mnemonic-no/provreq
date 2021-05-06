#!/usr/bin/env python3
"""Technique Show utility"""

import argparse
import sys
from typing import Dict, Text

import tabulate

from aep.tools import config


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("Show a technique")

    parser.add_argument("-t", "--technique", type=str, help="Technique to show")

    args = config.handle_args(parser, "show-technique")

    if not args.technique:
        sys.stderr.write("Specify technique with -t [TECHNIQUE_ID]\n")
        sys.exit(1)

    return args


def show_technique(technique: Dict[Text, Dict]) -> None:
    """Pretty print a technique"""

    headers = ["Provides", "Requires",
               "Tactic(s)", "Relevant", "Conditionals", "Subtechniques"]

    output = [["\n".join(technique['provides']),
               "\n".join(technique["requires"]),
               "\n".join(technique['tactic']),
               "\n".join(technique['relevant_for']),
               "\n".join(technique.get('conditional_provides', {}).keys()),
               "\n".join(x['name'] for x in technique.get('subtechniques', {}).values())]]

    print("+++")
    print("\t" + technique["name"])
    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))


def main():
    args = command_line_arguments()

    tech, _, _ = config.read_technique_promises(args)

    if not args.technique.startswith("T"):
        args.technique = "T" + args.technique

    show_technique(tech[args.technique])


if __name__ == "__main__":
    main()
