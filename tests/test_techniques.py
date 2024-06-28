import json

import provreq.tools.libs.data as data


def test_expand_subagents() -> None:

    agents = json.load(open("tests/data/agent_promises.json"))

    expanded = data.expand_agents(agents)

    assert len(expanded) == 349

    # Add the expanded subagents
    agents.update(expanded)

    expanded, expansion_map = data.create_conditional_agents(
        agents)

    assert len(expanded) == 139
    assert len(expansion_map) == 525
