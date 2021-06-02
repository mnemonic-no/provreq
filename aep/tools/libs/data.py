import copy
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Text, TextIO, Tuple

import tabulate


def expand_techniques(techniques: Dict) -> Dict:
    """Expand subtechniques -> techniques"""

    expanded = {}
    for k in techniques:
        for subtech in techniques[k]['subtechniques']:
            newtech = copy.deepcopy(techniques[k])
            newtech.pop('subtechniques')
            prefix = newtech['name']
            newtech.update(techniques[k]['subtechniques'][subtech])
            newtech['name'] = prefix + ":" + newtech['name']
            expanded.update({subtech: newtech})
    return expanded


def check_techniques(techniques: Dict) -> Tuple[List, bool]:
    """Check each technique description for the
    correct structure (must contain name, requires
    and provides"""

    missing = []
    ok = True
    req_keys = ["name", "requires", "provides", "conditional_provides"]
    for k, v in techniques.items():
        for rk in req_keys:
            if rk not in v:
                print(f"{k} missing key {rk}")
                missing.append((k, rk))
                ok = False
    return missing, ok


def check_promise_description(techniques: Dict, promise_description: Set[Text]) -> Set[Text]:
    """
    Get list of promise_description used in techniques
    that are not defined in condition vocabulary
    """

    missing = set()
    condition_keys = ["requires", "provides"]
    for _, technique in techniques.items():
        for key in condition_keys:
            missing.update([cond for cond in technique[key]
                            if cond not in promise_description])
    return missing


def read_promise_description_file(promise_description_file: TextIO) -> Set[Text]:
    """Read the pre and post condition descriptions"""

    return {row[0]
            for row in
            csv.reader(filter(
                # filter empty lines (commented out)
                lambda x: x != "",
                map(  # remove comments
                    lambda x: x.split("#")[0].strip(),
                    promise_description_file)))}


def print_condition_suggestion_and_die(missing_promise_description: Set[Text],
                                       promise_description: Set[Text]) -> None:
    """print_condition_suggestion_and_die tries to help the user find a
    possible misspelling, printing the suggestions and then terminate with
    exitcode 2"""

    sys.stderr.write("Conditions in techniques not specified in " +
                     "condition vocabulary\n")
    output_list = []
    for missing in missing_promise_description:
        possible_match = []
        for cond in promise_description:
            distance = levenshtein(missing, cond)
            possible_match.append((distance, cond))

        possible_match = sorted(possible_match)
        output_list.append([missing,
                            "\n".join(x[1]
                                      for x in possible_match[:3])])

    print(tabulate.tabulate(output_list,
                            headers=["condition", "perhaps you meant?"],
                            tablefmt="fancy_grid"))
    sys.exit(2)


def read_technique_promises(
        tech_promises_file: Path,
        promise_descriptions_file: Path,
        conditions_file: Path) -> Tuple[Dict, Dict, bool]:
    """Read the techniques file"""

    techniques: Dict = json.loads(open(tech_promises_file).read())
    _, ok = check_techniques(techniques)

    expanded = expand_techniques(techniques)
    techniques.update(expanded)

    with open(promise_descriptions_file) as pre_post_file:
        promise_description = read_promise_description_file(pre_post_file)

    # We need to check once for a match between the promise_description description
    # file and the techniques pre-conditional expansen to verify that the
    # system conditions used in conditional_provides is accidentally used in
    # provides and requires.
    missing_promise_description = check_promise_description(techniques, promise_description)
    if missing_promise_description:
        print_condition_suggestion_and_die(missing_promise_description, promise_description)

    created_conditional_tech, expand_map = create_conditional_techniques(
        techniques)
    techniques.update(created_conditional_tech)

    with open(conditions_file) as cond_file:
        conditions = read_promise_description_file(cond_file)

    # We check again, this time against the union of promise_description.csv and
    # conditions.csv as the system condtions is now used as provides and
    # requires based on the conditional_provides expansions.
    missing_promise_description = check_promise_description(
        techniques, promise_description.union(conditions))
    if missing_promise_description:
        print_condition_suggestion_and_die(missing_promise_description, promise_description)
        ok = False

    json.dump(techniques, open("test.json", "w"))

    return techniques, expand_map, ok


def read_tech_bundle(tech_bundle_file: Path, include_tool_techniques: bool = False) -> List[Text]:
    """ Read technique bundle from file """
    tech_bundle = json.loads(open(tech_bundle_file).read())

    # Should we include techniques inherited from tools used by threat actor?
    if include_tool_techniques:
        return list(set(tech_bundle["techniques"] + tech_bundle["tool_techniques"]))
    return list(set(tech_bundle["techniques"]))


def preprocess_techniques(
        technique_promises: Dict,
        expand_map: Dict,
        techniques: List[Text]) -> List[Text]:
    """
    Preprocess techniques:
        - remove techniques that no longer exist in techniques_promises
        - expand conditional techniques
    """

    techniques = remove_missing_techniques(technique_promises, techniques)
    techniques = expand_conditionals(expand_map, techniques)

    return techniques


def expand_conditionals(expand_map: Dict, techniques: List[Text]) -> List[Text]:
    """ Expand conditional techniques """
    techniques_conditionals = copy.deepcopy(techniques)

    for tat in techniques:
        if tat in expand_map:
            techniques_conditionals.extend(expand_map[tat])

    return techniques_conditionals


def levenshtein(a: Text, b: Text) -> int:
    "Calculates the Levenshtein distance between a and b."

    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = list(range(n+1))
    for i in range(1, m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1, n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def remove_missing_techniques(technique_promises: Dict,
                              techniques: List[Text]) -> List[Text]:
    """Check that all the techniques used by TA (as
    described in 'tech_bundle' is present in the techniques
    description and remove those that are not present"""

    # TODO: add logging if we remove techniques

    return [tech for tech in techniques if tech in technique_promises]


def create_conditional_techniques(techniques: Dict) -> Tuple[Dict, Dict]:
    """Expand conditional techniques"""

    # New conditional techniques created
    expanded = {}

    # a map used to extend the techniques used by a threat actor with
    # conditional techniques created runtime
    expansion_map = {}

    for k in techniques:
        expanded_conditions = []
        for conditional in techniques[k]['conditional_provides']:
            newtech = copy.deepcopy(techniques[k])
            newtech.pop('conditional_provides')
            newtech['name'] += f" [{conditional}]"
            newtech['requires'].append(conditional)
            newtech['provides'].extend(
                techniques[k]['conditional_provides'][conditional])
            newtech['requires'] = list(set(newtech['requires']))
            newtech['provides'] = list(set(newtech['provides']))
            new_id = k + "_" + conditional
            expanded.update({new_id: newtech})
            expanded_conditions.append(new_id)
        expansion_map[k] = expanded_conditions
    return expanded, expansion_map


def nop_techniques(techniques: Dict,
                   noped_promises: List[Text],
                   nop_empty_provides: bool = False) -> Set[Text]:
    """Get a list of noped techniques"""

    def _without(element: Text, lst: List[Text]) -> List[Text]:
        """remove an element from a list if presnet"""
        lst = list(set(copy.deepcopy(lst)))
        try:
            lst.remove(element)
        except ValueError:
            pass
        return lst

    nops = set()

    for tech in techniques:
        technique = copy.deepcopy(techniques[tech])
        for noped_promise in noped_promises:
            technique['requires'] = _without(
                noped_promise, technique['requires'])
            technique['provides'] = _without(
                noped_promise, technique['provides'])

        if nop_empty_provides:
            if not technique['provides']:
                nops.add(tech)
        else:
            if not technique['requires'] and not technique['provides']:
                nops.add(tech)

    return nops
