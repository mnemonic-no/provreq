import copy
from typing import Dict, List, Optional, Set, Text, Tuple, Union

from provreq.tools.libs.types import AttackStage, Simulation


def simulate(
    seeds: List[Text],
    agent_bundle: List[Text],
    agents: Dict,
    system_conditions: List[Text],
) -> Simulation:
    """Run the simulation"""

    sim = Simulation()

    sim.provided = set(seeds if seeds else []).union(set(system_conditions))
    pipeline, sim.backburner = fill_pipeline(agents, agent_bundle, sim.provided)
    if not pipeline:
        sim.debug.append("Pipeline not bootstrapped.")

    while pipeline:
        stage_agents: Set[Text] = set()
        stage_provides: Set[Text] = set()

        for agent_id in pipeline:
            stage_agents.add(agent_id)
            stage_provides.update(agents[agent_id]["provides"])

        sim.stages.append(
            AttackStage(
                new_provides=stage_provides.difference(sim.provided),
                last_stage_sum_provides=copy.deepcopy(sim.provided),
                agents=stage_agents,
            )
        )

        sim.provided.update(stage_provides)
        pipeline, sim.backburner = fill_pipeline(agents, sim.backburner, sim.provided)

    sim.objectives = {obj for obj in sim.provided if obj.startswith("objective_")}

    return sim


def fill_pipeline(
    agents: Dict, potensial: List[Text], provided: Set[Text]
) -> Tuple[List[Text], List[Text]]:
    """Run through all the agents not yet used by the ta
    (potensial) and put all the agents that has all requirements
    fullfilled into the pipeline. Techniques put into the pipleline is
    removed from the list of potensial agents."""

    mypotensial = copy.deepcopy(potensial)
    pipeline = []
    for agent in potensial:
        agent_ready = True
        for req in agents[agent]["requires"]:
            if req not in provided:
                agent_ready = False
        if agent_ready:
            pipeline.append(agent)
            mypotensial.remove(agent)

    return pipeline, mypotensial


def stage_agent(
    agent: Dict, last_stage_sum_provides: Set[Text], show_agent_classes: bool
) -> Text:
    """Get description of agent"""

    description: Text = agent["name"]
    agent_classes = agent.get("agent_class", [])

    # Append comma seprated list of agent_classes after agent name
    if show_agent_classes and agent_classes:
        description += " (" + ",".join(agent_classes) + ")"

    if all(provides in last_stage_sum_provides for provides in agent["provides"]):
        description += " [*]"

    return description


def format_list(rows: List, join_text: Optional[Text]) -> Union[Text, List]:
    """Join list using `join_text` if specified, otherwise return list as is"""
    if join_text:
        return join_text.join(rows)
    return rows


def stages_table(
    sim: Simulation,
    agents: Dict,
    show_promises: bool = False,
    show_agent_classes: bool = False,
    join_text: Optional[Text] = "\n",
) -> List[Dict]:
    """
    Return formated stages in a simulartion, optionally
    enriched with promises and agent_classes
    """

    table = []

    for idx, stage in enumerate(sim.stages):
        stage_agent_classes: Set[Text] = set()
        agent_descriptions: Set[Text] = set()

        for agent_id in stage.agents:

            if agent_id.startswith("_"):
                # Skip shadow agents
                continue

            agent = agents[agent_id]
            stage_agent_classes.update(agent.get("agent_class", []))
            agent_descriptions.add(
                stage_agent(agent, stage.last_stage_sum_provides, show_agent_classes)
            )

        row = {
            "stage": idx + 1,
            "agents": format_list(sorted(agent_descriptions), join_text),
        }

        if show_promises:
            row["new promises @end-of-stage"] = format_list(
                sorted(stage.new_provides), join_text
            )

        if show_agent_classes:
            row["agent_classes"] = format_list(sorted(stage_agent_classes), join_text)

        table.append(row)

    return table
