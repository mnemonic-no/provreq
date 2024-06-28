#!/usr/bin/env python3
"""Technique Show utility"""

import argparse
import sys
from collections import defaultdict
from typing import Dict, Text

import tabulate

from provreq.tools import config


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("Show promises")

    parser.add_argument("--promise", type=str, help="Show how this promise is used")

    args = config.handle_args(parser, "show-promise")

    if not args.promise:
        sys.stderr.write("Specify promise with --promise [PROMISE]\n")
        sys.exit(1)

    return args


def show_promise(promise: Text, agents: Dict[Text, Dict]) -> None:
    """Create stats and show a promise"""

    agents_provides = set()
    agents_requires = set()

    agent_classes_provides = defaultdict(int)
    agent_classes_requires = defaultdict(int)

    conditional_provides = set()

    for tid, agent in agents.items():
        for cond_prov in agent.get("conditional_provides", {}).values():
            if promise in cond_prov:
                conditional_provides.add((tid, agent["name"]))

        if promise in agent.get("provides", []):
            agents_provides.add((tid, agent["name"]))
            for tac in agent["agent_class"]:
                agent_classes_provides[tac] += 1
        if promise in agent.get("requires", []):
            agents_requires.add((tid, agent["name"]))
            for tac in agent["agent_class"]:
                agent_classes_requires[tac] += 1

    print("+++")
    print("Usage")

    headers = ["Provides", "Requires"]
    output = [
        [
            "\n".join(f"{tid}: {name}" for tid, name in agents_provides),
            "\n".join(f"{tid}: {name}" for tid, name in agents_requires),
        ]
    ]
    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))

    agent_classes = set()
    agent_classes.update(set(agent_classes_provides.keys()))
    agent_classes.update(set(agent_classes_requires.keys()))

    headers = ["Tactic", "Provides", "Requires"]
    output = []
    for agent_class in agent_classes:
        output.append(
            [agent_class, agent_classes_provides.get(agent_class, 0), agent_classes_requires.get(agent_class, 0)]
        )
    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))
    print(f"Provided by {len(conditional_provides)} conditional provides")


def main():

    args = command_line_arguments()

    agent, _, _ = config.read_agent_promises(args)

    show_promise(args.promise, agent)


if __name__ == "__main__":
    main()
