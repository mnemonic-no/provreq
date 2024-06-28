import copy
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Text, TextIO, Tuple

import tabulate


def expand_agents(agents: Dict) -> Dict:
    """Expand children -> agents"""

    expanded = {}
    for k in agents:
        for child in agents[k]["children"]:
            newagent = copy.deepcopy(agents[k])
            newagent.pop("children")
            prefix = newagent["name"]
            newagent.update(agents[k]["children"][child])
            newagent["name"] = prefix + ":" + newagent["name"]
            expanded.update({child: newagent})
    return expanded


def check_agents(agents: Dict) -> Tuple[List, bool]:
    """Check each agent description for the
    correct structure (must contain name, requires
    and provides"""

    missing = []
    ok = True
    req_keys = ["name", "requires", "provides", "conditional_provides"]
    for k, v in agents.items():
        for rk in req_keys:
            if rk not in v:
                print(f"{k} missing key {rk}")
                missing.append((k, rk))
                ok = False
    return missing, ok


def check_promise_description(
    agents: Dict, promise_description: Set[Text]
) -> Set[Text]:
    """
    Get list of promise_description used in agents
    that are not defined in condition vocabulary
    """

    missing = set()
    condition_keys = ["requires", "provides"]
    for _, agent in agents.items():
        for key in condition_keys:
            missing.update(
                [cond for cond in agent[key] if cond not in promise_description]
            )
    return missing


def read_promise_description_file(promise_description_file: TextIO) -> Set[Text]:
    """Read the pre and post condition descriptions"""

    return {
        row[0]
        for row in csv.reader(
            filter(
                # filter empty lines (commented out)
                lambda x: x != "",
                map(  # remove comments
                    lambda x: x.split("#")[0].strip(), promise_description_file
                ),
            )
        )
    }


def print_condition_suggestion_and_die(
    missing_promise_description: Set[Text], promise_description: Set[Text]
) -> None:
    """print_condition_suggestion_and_die tries to help the user find a
    possible misspelling, printing the suggestions and then terminate with
    exitcode 2"""

    sys.stderr.write(
        "Conditions in agents not specified in " + "condition vocabulary\n"
    )
    output_list = []
    for missing in missing_promise_description:
        possible_match = []
        for cond in promise_description:
            distance = levenshtein(missing, cond)
            possible_match.append((distance, cond))

        possible_match = sorted(possible_match)
        output_list.append([missing, "\n".join(x[1] for x in possible_match[:3])])

    print(
        tabulate.tabulate(
            output_list,
            headers=["condition", "perhaps you meant?"],
            tablefmt="fancy_grid",
        )
    )
    sys.exit(2)


def read_agent_promises(
    agent_promises_file: Path, promise_descriptions_file: Path, conditions_file: Path
) -> Tuple[Dict, Dict, bool]:
    """Read the agents file"""

    agents: Dict = json.loads(open(agent_promises_file).read())
    _, ok = check_agents(agents)

    expanded = expand_agents(agents)
    agents.update(expanded)

    with open(promise_descriptions_file) as pre_post_file:
        promise_description = read_promise_description_file(pre_post_file)

    # We need to check once for a match between the promise_description description
    # file and the agents pre-conditional expansen to verify that the
    # system conditions used in conditional_provides is accidentally used in
    # provides and requires.
    missing_promise_description = check_promise_description(agents, promise_description)
    if missing_promise_description:
        print_condition_suggestion_and_die(
            missing_promise_description, promise_description
        )

    created_conditional_agent, expand_map = create_conditional_agents(agents)
    agents.update(created_conditional_agent)

    with open(conditions_file) as cond_file:
        conditions = read_promise_description_file(cond_file)

    # We check again, this time against the union of promise_description.csv and
    # conditions.csv as the system condtions is now used as provides and
    # requires based on the conditional_provides expansions.
    missing_promise_description = check_promise_description(
        agents, promise_description.union(conditions)
    )
    if missing_promise_description:
        print_condition_suggestion_and_die(
            missing_promise_description, promise_description
        )
        ok = False

    json.dump(agents, open("test.json", "w"))

    return agents, expand_map, ok


def read_agent_bundle(
    agent_bundle_file: Path, include_extended_agents: bool = False
) -> List[Text]:
    """Read agent bundle from file"""
    agent_bundle = json.loads(open(agent_bundle_file).read())

    # Should we include agents inherited from extended agents?
    if include_extended_agents:
        return list(set(agent_bundle["agents"] + agent_bundle["extended_agents"]))
    return list(set(agent_bundle["agents"]))


def preprocess_agents(
    agent_promises: Dict, expand_map: Dict, agents: List[Text]
) -> List[Text]:
    """
    Preprocess agents:
        - remove agents that no longer exist in agents_promises
        - expand conditional agents
    """

    agents = remove_missing_agents(agent_promises, agents)
    agents = expand_conditionals(expand_map, agents)

    return agents


def expand_conditionals(expand_map: Dict, agents: List[Text]) -> List[Text]:
    """Expand conditional agents"""
    agents_conditionals = copy.deepcopy(agents)

    for tat in agents:
        if tat in expand_map:
            agents_conditionals.extend(expand_map[tat])

    return agents_conditionals


def levenshtein(a: Text, b: Text) -> int:
    "Calculates the Levenshtein distance between a and b."

    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = list(range(n + 1))
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def remove_missing_agents(agent_promises: Dict, agents: List[Text]) -> List[Text]:
    """Check that all the agents used by TA (as
    described in 'agent_bundle' is present in the agents
    description and remove those that are not present"""

    # TODO: add logging if we remove agents

    return [agent for agent in agents if agent in agent_promises]


def create_conditional_agents(agents: Dict) -> Tuple[Dict, Dict]:
    """Expand conditional agents"""

    # New conditional agents created
    expanded = {}

    # a map used to extend the agents used by a threat actor with
    # conditional agents created runtime
    expansion_map = {}

    for k in agents:
        expanded_conditions = []
        for conditional in agents[k]["conditional_provides"]:
            newagent = copy.deepcopy(agents[k])
            newagent.pop("conditional_provides")
            newagent["name"] += f" [{conditional}]"
            newagent["requires"].append(conditional)
            newagent["provides"].extend(agents[k]["conditional_provides"][conditional])
            newagent["requires"] = list(set(newagent["requires"]))
            newagent["provides"] = list(set(newagent["provides"]))
            new_id = k + "_" + conditional
            expanded.update({new_id: newagent})
            expanded_conditions.append(new_id)
        expansion_map[k] = expanded_conditions
    return expanded, expansion_map


def nop_agents(
    agents: Dict, noped_promises: List[Text], nop_empty_provides: bool = False
) -> Set[Text]:
    """Get a list of noped agents"""

    def _without(element: Text, lst: List[Text]) -> List[Text]:
        """remove an element from a list if presnet"""
        lst = list(set(copy.deepcopy(lst)))
        try:
            lst.remove(element)
        except ValueError:
            pass
        return lst

    nops = set()

    for agent_name in agents:
        agent = copy.deepcopy(agents[agent_name])
        for noped_promise in noped_promises:
            agent["requires"] = _without(noped_promise, agent["requires"])
            agent["provides"] = _without(noped_promise, agent["provides"])

        if nop_empty_provides:
            if not agent["provides"]:
                nops.add(agent_name)
        else:
            if not agent["requires"] and not agent["provides"]:
                nops.add(agent_name)

    return nops
