#!/usr/bin/env python3

import argparse
import sys
from typing import Dict, List, Text

import tabulate

from provreq.tools import config

"""Techniques Search utility"""


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("Search agents")

    parser.add_argument(
        "-p",
        "--provides",
        type=config.split_arg,
        help="Search for agents providing these promises",
    )
    parser.add_argument(
        "-np",
        "--notprovides",
        type=config.split_arg,
        help="Search for agents that does _not_ provide promises",
    )
    parser.add_argument(
        "-r",
        "--requires",
        type=config.split_arg,
        help="Search for agents requires these promises",
    )
    parser.add_argument(
        "-nr",
        "--notrequires",
        type=config.split_arg,
        help="Search for agents that does _not_ require promises",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=config.split_arg,
        help="Search for agents whos name contains this string",
    )

    args = config.handle_args(parser, "promise-search")

    if not (
        args.provides
        or args.notprovides
        or args.requires
        or args.notrequires
        or args.name
    ):
        sys.stderr.write("Specify at least one search option\n")
        sys.exit(1)

    return args


def show_agents(agents: Dict[Text, Dict]) -> None:
    headers = ["ID", "Name", "Tactic(s)"]

    output = [(k, v["name"], "\n".join(v["agent_class"])) for k, v in agents.items()]

    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))
    print(f"n={len(output)}")


def contains(search_terms: List[Text], bucket: List[Text]) -> bool:
    """Check if one or more of the search_terms are in a bucket"""

    for search_term in search_terms:
        for item in bucket:
            if search_term in item:
                break
        else:
            return False
    return True


def main():

    args = command_line_arguments()

    agent, _, _ = config.read_agent_promises(args)

    if args.provides:
        agent = {k: v for k, v in agent.items() if contains(args.provides, v["provides"])}

    if args.notprovides:
        agent = {
            k: v
            for k, v in agent.items()
            if not contains(args.notprovides, v["provides"])
        }

    if args.requires:
        agent = {k: v for k, v in agent.items() if contains(args.requires, v["requires"])}

    if args.notrequires:
        agent = {
            k: v
            for k, v in agent.items()
            if not contains(args.notrequires, v["requires"])
        }

    if args.name:
        agent = {
            k: v
            for k, v in agent.items()
            if any(name in v["name"].lower() for name in args.name)
        }

    show_agents(agent)


if __name__ == "__main__":
    main()
