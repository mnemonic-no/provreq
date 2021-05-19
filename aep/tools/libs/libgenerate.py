import copy
from typing import Dict, List, Optional, Set, Text, Tuple, Union

from aep.tools.libs.types import AttackStage, Simulation


def simulate(seeds: List[Text],
             tech_bundle: List[Text],
             techniques: Dict,
             system_conditions: List[Text]) -> Simulation:
    """Run the simulation"""

    sim = Simulation()

    sim.provided = set(seeds if seeds else []).union(set(system_conditions))
    pipeline, sim.backburner = fill_pipeline(
        techniques, tech_bundle, sim.provided)
    if not pipeline:
        sim.debug.append("Pipeline not bootstrapped.")

    while pipeline:
        stage_techniques: Set[Text] = set()
        stage_provides: Set[Text] = set()

        for tech_id in pipeline:
            stage_techniques.add(tech_id)
            stage_provides.update(techniques[tech_id]["provides"])

        sim.stages.append(
            AttackStage(
                new_provides=stage_provides.difference(sim.provided),
                last_stage_sum_provides=copy.deepcopy(sim.provided),
                techniques=stage_techniques,
            ))

        sim.provided.update(stage_provides)
        pipeline, sim.backburner = fill_pipeline(
            techniques, sim.backburner, sim.provided)

    sim.objectives = {
        obj for obj in sim.provided if obj.startswith("objective_")}

    return sim


def fill_pipeline(techniques: Dict,
                  potensial: List[Text],
                  provided: Set[Text]) -> Tuple[List[Text], List[Text]]:
    """Run through all the techniques not yet used by the ta
    (potensial) and put all the techniques that has all requirements
    fullfilled into the pipeline. Techniques put into the pipleline is
    removed from the list of potensial techniques."""

    mypotensial = copy.deepcopy(potensial)
    pipeline = []
    for tech in potensial:
        tech_ready = True
        for req in techniques[tech]["requires"]:
            if req not in provided:
                tech_ready = False
        if tech_ready:
            pipeline.append(tech)
            mypotensial.remove(tech)

    return pipeline, mypotensial


def stage_technique(
        technique: Dict,
        last_stage_sum_provides: Set[Text],
        show_tactics: bool) -> Text:
    """ Get description of technique """

    description: Text = technique["name"]
    tactics = technique.get("tactic", [])

    # Append comma seprated list of tactics after technique name
    if show_tactics and tactics:
        description += " (" + ",".join(tactics) + ")"

    if all(provides in last_stage_sum_provides
           for provides in technique["provides"]):
        description += " [*]"

    return description


def format_list(rows: List, join_text: Optional[Text]) -> Union[Text, List]:
    """ Join list using `join_text` if specified, otherwise return list as is """
    if join_text:
        return join_text.join(rows)
    return rows


def stages_table(
        sim: Simulation,
        techniques: Dict,
        show_promises: bool = False,
        show_tactics: bool = False,
        join_text: Optional[Text] = "\n") -> List[Dict]:
    """
    Return formated stages in a simulartion, optionally
    enriched with promises and tactics
    """

    table = []

    for idx, stage in enumerate(sim.stages):
        stage_tactics: Set[Text] = set()
        tech_descriptions: Set[Text] = set()

        for tech_id in stage.techniques:

            if tech_id.startswith("_"):
                # Skip shadow techniques
                continue

            technique = techniques[tech_id]
            stage_tactics.update(technique.get("tactic", []))
            tech_descriptions.add(
                stage_technique(
                    technique,
                    stage.last_stage_sum_provides,
                    show_tactics))

        row = {
            "stage": idx+1,
            "techniques": format_list(sorted(tech_descriptions), join_text),
        }

        if show_promises:
            row["new promises @end-of-stage"] = format_list(
                sorted(stage.new_provides), join_text)

        if show_tactics:
            row["tactics"] = format_list(sorted(stage_tactics), join_text)

        table.append(row)

    return table
