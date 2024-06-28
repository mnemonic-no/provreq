import provreq.tools.libs.data as data

agents = {
    "test1": {
        "name": "test1",
        "requires": [],
        "provides": ["test_prom1"],
        "conditional_provides": {}
    },
    "test2": {
        "name": "test2",
        "requires": ["test_prom1"],
        "provides": ["test_prom2"],
        "conditional_provides": {}
    }
}

bad_agents = {
    "test1": {
        "name": "test1",
        "provides": ["test_prom1"]
    },
    "test2": {
        "name": "test2",
        "requires": ["test_prom1"],
    }
}


def test_check_agents():

    missing, ok = data.check_agents(agents)
    assert ok
    assert not missing

    missing, ok = data.check_agents(bad_agents)
    assert not ok
    assert missing


def test_missing_agents():

    original = ["test1", "test2"]
    filtered = data.remove_missing_agents(agents, original)
    assert filtered == original

    filtered = data.remove_missing_agents(agents, original + ["test3"])
    assert filtered == original
