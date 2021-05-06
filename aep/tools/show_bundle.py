#!/usr/bin/env python3

"""Pretty print Threat Actor file"""

import argparse
import sys
from collections import OrderedDict
from pathlib import Path

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

    args: argparse.Namespace = config.handle_args(parser, "show-bundle")

    if not args.technique_bundle:
        sys.stderr.write("--technique-bundle must be specified\n")
        sys.exit(1)

    return args


def main():
    """main entry"""

    args = command_line_arguments()

    tactics = OrderedDict()
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


    # Expand subtechniques -> techniques
    expanded = {}
    # for k in techniques:
    #    for subtech in techniques[k]['subtechniques']:
    #        newtech = techniques[k].copy()
    #        newtech.pop('subtechniques')
    #        prefix = newtech['name']
    #        newtech.update(techniques[k]['subtechniques'][subtech])
    #        newtech['name'] = prefix + ":" + newtech['name']
    #        expanded.update({subtech: newtech})
    # techniques.update(expanded)

    for tech in tech_bundle:
        tech_dict = techniques[tech]
        for tactic in tech_dict["tactic"]:
            tactics[tactic].append(
                f'{tech[:10]} [{tech_dict["name"][:10]}...]')

    print(tabulate.tabulate(tactics,
                            headers=tactics.keys(),
                            tablefmt="fancy_grid"))


if __name__ == "__main__":
    main()
