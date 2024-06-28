#!/usr/bin/env python3

"""Simulate a "run" through the agents used by a threat
actor"""

import argparse
import sys
from pathlib import Path

import tabulate

from provreq.tools import config
from provreq.tools.libs.data import nop_agents
from provreq.tools.libs.libgenerate import simulate, stages_table


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
        "--seeds", type=config.split_arg, help="Entry conditions 'already in place'"
    )
    parser.add_argument(
        "--end-condition",
        type=str,
        default="objective_exfiltration",
        help="What condition is the desired outcome",
    )
    parser.add_argument(
        "--include-agents",
        type=config.split_arg,
        help="Include the following agents in the "
        "simulation as accessible to the attacker",
    )
    parser.add_argument(
        "--exclude-agents",
        type=config.split_arg,
        help=(
            "Exclude the following agents from "
            "the simulation even if accessible to "
            "the attacker"
        ),
    )
    parser.add_argument(
        "--show-promises",
        action="store_true",
        help="Show available promises on each stage",
    )
    parser.add_argument(
        "--show-agent_classes",
        action="store_true",
        help="Show agent_classes in paranthesis after agents "
        "and the set of all agent_classes at each stage in a column",
    )
    parser.add_argument(
        "--nop-empty-provides",
        action="store_true",
        help="Do not check requires for empty list. "
        "Remove agents with empty provides only.",
    )
    parser.add_argument(
        "--include-extended-agents",
        action="store_true",
        help="Include agents for threat actor that "
        "is inherited from extended agents used",
    )
    parser.add_argument(
        "--system-conditions",
        type=config.split_arg,
        help="List of conditions related to the "
        "system (e.g. poor_security_practices)",
    )

    args: argparse.Namespace = config.handle_args(parser, "generate")

    if not args.agent_bundle:
        sys.stderr.write("--agent-bundle must be specified\n")
        sys.exit(1)

    return args


def main() -> None:
    """main program loop"""

    args = command_line_arguments()

    agents, agent_bundle = config.read_data(args)

    nops = nop_agents(agents, ["defense_evasion"], args.nop_empty_provides)
    removed = []
    for tat in agent_bundle[:]:
        if tat in nops:
            removed.append(tat)
            agent_bundle.remove(tat)
    print(f"Removed {len(removed)} NOP agents: {sorted(removed)}")

    if args.include_agents:
        agent_bundle.extend(args.include_agents)
    if args.exclude_agents:
        for exclude in args.exclude_agents:
            try:
                agent_bundle.remove(exclude)
            except ValueError:
                print(f"{sorted(exclude)} is not in the list of agents used")

    sim = simulate(
        args.seeds,
        agent_bundle,
        agents,
        args.system_conditions if args.system_conditions else {},
    )

    table = stages_table(sim, agents, args.show_promises, args.show_agent_classes)

    print(tabulate.tabulate(table, headers="keys", tablefmt="fancy_grid"))

    print("[*] Technique does not provide any new promises")

    if sim.objectives:
        print(f"The following objectives where reached: {sorted(sim.objectives)}")

    if args.end_condition in sim.provided:
        print(
            f"SUCCESS: Attack chain exited with "
            f"end condition '{args.end_condition}'"
        )
    else:
        print(
            f"FAIL: incomplete attack chain, "
            f"could not achieve end condition: {args.end_condition}"
        )


if __name__ == "__main__":
    main()
