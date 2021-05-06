import copy
from typing import Dict, List, Set, Text, Tuple

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
