#!/usr/bin/env python3

"""Simulate a "run" through the techniques used by a threat
actor"""

import argparse
import sys
from pathlib import Path

import tabulate

from aep.tools import config
from aep.tools.libs.data import nop_techniques
from aep.tools.libs.libgenerate import simulate, stages_table


def command_line_arguments() -> argparse.Namespace:
    """Parse the command line arguments"""

    parser = config.common_args("ATT&CK simulator")

    parser.add_argument(
        "-b",
        "--technique-bundle",
        type=Path,
        help="The threat actor file to simulate",
    )

    parser.add_argument('--seeds', type=config.split_arg,
                        help="Entry conditions 'already in place'")
    parser.add_argument('--end-condition', type=str,
                        default="objective_exfiltration",
                        help="What condition is the desired outcome")
    parser.add_argument('--include-techniques', type=config.split_arg,
                        help="Include the following techniques in the "
                             "simulation as accessible to the attacker")
    parser.add_argument('--exclude-techniques', type=config.split_arg,
                        help=("Exclude the following techniques from "
                              "the simulation even if accessible to "
                              "the attacker"))
    parser.add_argument('--show-promises', action='store_true',
                        help="Show available promises on each stage")
    parser.add_argument('--show-tactics', action='store_true',
                        help="Show tactics in paranthesis after techniques "
                             "and the set of all tactics at each stage in a column")
    parser.add_argument('--nop-empty-provides', action='store_true',
                        help="Do not check requires for empty list. "
                             "Remove techniques with empty provides only.")
    parser.add_argument('--include-tools', action='store_true',
                        help="Include techniques for threat actor that "
                             "is inherited from tools used")
    parser.add_argument('--system-conditions', type=config.split_arg,
                        help="List of conditions related to the "
                             "system (e.g. poor_security_practices)")

    args: argparse.Namespace = config.handle_args(parser, "generate")

    if not args.technique_bundle:
        sys.stderr.write("--technique-bundle must be specified\n")
        sys.exit(1)

    return args


def main() -> None:
    """main program loop"""

    args = command_line_arguments()

    techniques, tech_bundle = config.read_data(args)

    nops = nop_techniques(
        techniques, ['defense_evasion'], args.nop_empty_provides)
    removed = []
    for tat in tech_bundle[:]:
        if tat in nops:
            removed.append(tat)
            tech_bundle.remove(tat)
    print(f"Removed {len(removed)} NOP techniques: {sorted(removed)}")

    if args.include_techniques:
        tech_bundle.extend(args.include_techniques)
    if args.exclude_techniques:
        for exclude in args.exclude_techniques:
            try:
                tech_bundle.remove(exclude)
            except ValueError:
                print(f"{sorted(exclude)} is not in the list of techniques used")

    sim = simulate(
        args.seeds,
        tech_bundle,
        techniques,
        args.system_conditions if args.system_conditions else {}
    )

    table = stages_table(
        sim,
        techniques,
        args.show_promises,
        args.show_tactics)

    print(tabulate.tabulate(table, headers="keys", tablefmt="fancy_grid"))

    print("[*] Technique does not provide any new promises")

    if sim.objectives:
        print(
            f"The following objectives where reached: {sorted(sim.objectives)}")

    if args.end_condition in sim.provided:
        print(f"SUCCESS: Attack chain exited with "
              f"end condition '{args.end_condition}'")
    else:
        print(f"FAIL: incomplete attack chain, "
              f"could not achieve end condition: {args.end_condition}")


if __name__ == "__main__":
    main()
