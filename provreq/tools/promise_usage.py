#!/usr/bin/env python3

import argparse
import csv
from collections import defaultdict

import tabulate

from provreq.tools import config


def command_line_arguments() -> argparse.Namespace:
    """parse the command line arguments"""

    parser = config.common_args("Show little or unused promises")

    parser.add_argument(
        "-rl",
        "--requirelimit",
        type=int,
        default=0,
        help="Show promises with required count " "less than or equal to this",
    )
    parser.add_argument(
        "-pl",
        "--providelimit",
        type=int,
        default=0,
        help="Show promises with provided count " "less than or equal to this",
    )

    return config.handle_args(parser, "promise-usage")


def main() -> None:
    """main entry point"""

    args = command_line_arguments()

    prepost = {
        promise: desc
        for promise, desc in csv.reader(
            open(args.data_dir / args.promise_descriptions), escapechar="\\"
        )
    }

    provides = defaultdict(int)
    requires = defaultdict(int)

    for prom in prepost:
        provides[prom] = 0
        requires[prom] = 0

    agents, _, _ = config.read_agent_promises(args)

    for agent in agents.values():
        for provide in agent["provides"]:
            provides[provide] += 1
        for require in agent["requires"]:
            requires[require] += 1

    output = set()
    for provide, count in provides.items():
        if count <= args.providelimit:
            output.add((provide, provides[provide], requires[provide]))
    for require, count in requires.items():
        if count <= args.requirelimit:
            output.add((require, provides[require], requires[require]))

    outputlist = [list(x) for x in output]

    print(
        tabulate.tabulate(
            outputlist,
            headers=["promise", "provides", "requires"],
            tablefmt="fancy_grid",
        )
    )


if __name__ == "__main__":
    main()
