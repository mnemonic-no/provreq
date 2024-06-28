#!/usr/bin/env python3
"""agent Show utility"""

import argparse
import sys
from typing import Dict, Text

import tabulate

from provreq.tools import config


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("Show a agent")

    parser.add_argument("-t", "--agent", type=str, help="agent to show")

    args = config.handle_args(parser, "show-agent")

    if not args.agent:
        sys.stderr.write("Specify agent with -t [agent_ID]\n")
        sys.exit(1)

    return args


def show_agent(agent: Dict[Text, Dict]) -> None:
    """Pretty print a agent"""

    headers = [
        "Provides",
        "Requires",
        "agent_class(s)",
        "Relevant",
        "Conditionals",
        "Children",
    ]

    output = [
        [
            "\n".join(agent["provides"]),
            "\n".join(agent["requires"]),
            "\n".join(agent["agent_class"]),
            "\n".join(agent["relevant_for"]),
            "\n".join(agent.get("conditional_provides", {}).keys()),
            "\n".join(x["name"] for x in agent.get("subagents", {}).values()),
        ]
    ]

    print("+++")
    print("\t" + agent["name"])
    print(tabulate.tabulate(output, headers=headers, tablefmt="fancy_grid"))


def main():
    args = command_line_arguments()

    agent, _, _ = config.read_agent_promises(args)

    if not args.agent.startswith("T"):
        args.agent = "T" + args.agent

    show_agent(agent[args.agent])


if __name__ == "__main__":
    main()
