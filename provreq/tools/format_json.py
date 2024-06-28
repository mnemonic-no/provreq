#!/usr/bin/env python3

import json
import sys
from typing import Dict, Text


def check_unreachable(agents: Dict[Text, Dict]) -> bool:
    """Check for agents that can not be reached without seeding the simulation
    e.g. no agents provides the promise a agent requires"""

    normal_provides = set()
    conditional_provides = set()

    ok = True

    # Genereate a list of all provided promises in agents, children and
    # conditional provides
    for agent in agents.values():
        normal_provides.update(set(agent["provides"]))
        if agent["children"]:
            for child in agent["children"].values():
                normal_provides.update(set(child.get("provides", [])))
        if agent["conditional_provides"]:
            for provides in agent["conditional_provides"]:
                conditional_provides.update(set(provides))

    with_conditional_provides = set()
    with_conditional_provides.update(normal_provides)
    with_conditional_provides.update(conditional_provides)

    # Run through all agents to check if what they require is actually provided by 'something'
    for tid, agent in agents.items():
        if not all(req in normal_provides for req in agent["requires"]):
            if all(req in with_conditional_provides for req in agent["requires"]):
                print(
                    f"Warning: {tid} can only be reached through conditional provides"
                )
            else:
                print(f"Warning: {tid} can not be reached without seeding")
                ok = False

        for stid, child in agent["children"].items():
            if not all(req in normal_provides for req in child.get("requires", [])):
                if all(
                    req in with_conditional_provides
                    for req in child.get("requires", [])
                ):
                    print(
                        f"Warning: {stid} can only be reached through conditional provides"
                    )
                else:
                    print(f"Warning: {stid} can not be reached without seeding")
                    ok = False

    return ok


def sorted_unique_list(objects: Dict[Text, Dict]) -> Dict[Text, Dict]:
    """sorted_unique_list is a helper function passed to the json loader to
    ensure that all elements of list type in the dictionary is both sorted and
    only occuring once"""

    return {
        key: sorted(list(set(value))) if isinstance(value, list) else value
        for key, value in objects.items()
    }


def main() -> None:
    """main entry point"""

    data = json.load(open(sys.argv[1]), object_hook=sorted_unique_list)
    _ = check_unreachable(data)
    json.dump(data, open(sys.argv[1], "w"), indent="    ", sort_keys=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} [JSONFILE]")
        print(
            "Formats the json with sorted keys, sorted (unique) lists and proper indents"
        )
    else:
        main()
