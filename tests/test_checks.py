import aep.tools.libs.data as data

techniques = {
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

bad_techniques = {
    "test1": {
        "name": "test1",
        "provides": ["test_prom1"]
    },
    "test2": {
        "name": "test2",
        "requires": ["test_prom1"],
    }
}


def test_check_techniques():

    missing, ok = data.check_techniques(techniques)
    assert ok
    assert not missing

    missing, ok = data.check_techniques(bad_techniques)
    assert not ok
    assert missing


def test_missing_techniques():
    missing, ok = data.find_missing_techniques(
        techniques, ["test1", "test2"])
    assert ok
    assert not missing

    missing, ok = data.find_missing_techniques(
        techniques, ["test1", "test2", "test3"])
    assert not ok
    assert "test3" in missing
    assert len(missing) == 1
