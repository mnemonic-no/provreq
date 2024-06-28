import pytest

import provreq.tools.libs.data as data


def test_expand_agents():

    test_agents = {
        "T1": {
            "conditional_provides": {
                "conditional_require1": [
                    "conditional_promise1",
                    "conditional_promise2",
                ],
                "conditional_require2": ["conditional_promise2"],
            },
            "mitigations": ["mitigation1"],
            "name": "Test Tech",
            "provides": ["promise1", "promise2"],
            "relevant_for": ["testing"],
            "requires": ["promise0"],
            "children": {
                "T1.001": {"name": "Threat Intel Vendors", "provides": []},
                "T1.002": {
                    "name": "Purchase Technical Data",
                    "requires": ["promise3", "promise4"],
                },
            },
            "agent_class": ["Testing"],
        }
    }

    assert len(test_agents) == 1
    children = data.expand_agents(test_agents)
    test_agents.update(children)

    assert len(test_agents) == 3
    assert len(children) == 2

    cond_agent, cond_agent_exp_map = data.create_conditional_agents(test_agents)

    assert len(cond_agent) == 6
    assert len(cond_agent_exp_map) == 3

    test_agents.update(cond_agent)

    assert len(test_agents) == 9

    assert "T1" in test_agents
    assert "T1.001" in test_agents
    assert "T1.002" in test_agents

    assert "T1_conditional_require1" in test_agents
    assert "T1_conditional_require2" in test_agents

    assert "T1.001_conditional_require1" in test_agents
    assert "T1.001_conditional_require2" in test_agents

    assert "T1.002_conditional_require1" in test_agents
    assert "T1.002_conditional_require2" in test_agents
