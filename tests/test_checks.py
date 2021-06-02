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

    original = ["test1", "test2"]
    filtered = data.remove_missing_techniques(techniques, original)
    assert filtered == original

    filtered = data.remove_missing_techniques(techniques, original + ["test3"])
    assert filtered == original
