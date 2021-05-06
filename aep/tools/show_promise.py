#!/usr/bin/env python3
"""Technique Show utility"""

import argparse
import sys
from collections import defaultdict
from typing import Dict, Text

import tabulate

from aep.tools import config


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("Show promises")

    parser.add_argument("--promise", type=str,
                        help="Show how this promise is used")


    args = config.handle_args(parser, "show-promise")

    if not args.promise:
        sys.stderr.write("Specify promise with --promise [PROMISE]\n")
        sys.exit(1)

    return args


def show_promise(promise: Text, techniques: Dict[Text, Dict]) -> None:
    """Create stats and show a promise"""

    techniques_provides = set()
    techniques_requires = set()

    tactics_provides = defaultdict(int)
    tactics_requires = defaultdict(int)

    conditional_provides = set()

    for tid, tech in techniques.items():
        for cond_prov in tech.get("conditional_provides", {}).values():
            if promise in cond_prov:
                conditional_provides.add((tid, tech['name']))

        if promise in tech.get('provides', []):
            techniques_provides.add((tid, tech['name']))
            for tac in tech['tactic']:
                tactics_provides[tac] += 1
        if promise in tech.get('requires', []):
            techniques_requires.add((tid, tech['name']))
            for tac in tech['tactic']:
                tactics_requires[tac] += 1

    print("+++")
    print("Usage")

    headers = ['Provides', 'Requires']
    output = [["\n".join(f"{tid}: {name}" for tid, name in techniques_provides),
               "\n".join(f"{tid}: {name}" for tid, name in techniques_requires)]]
    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))

    tactics = set()
    tactics.update(set(tactics_provides.keys()))
    tactics.update(set(tactics_requires.keys()))

    headers = ['Tactic', 'Provides', 'Requires']
    output = []
    for tactic in tactics:
        output.append([tactic,
                       tactics_provides.get(tactic, 0),
                       tactics_requires.get(tactic, 0)])
    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))
    print(f"Provided by {len(conditional_provides)} conditional provides")


def main():

    args = command_line_arguments()

    tech, _, _ = config.read_technique_promises(args)

    show_promise(args.promise, tech)


if __name__ == "__main__":
    main()
