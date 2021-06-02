"""Test for generate.py"""

import io
from pathlib import Path

import aep.tools.libs.data as data


def test_read_files() -> None:

    technique_promises, expand_map, ok = data.read_technique_promises(
        Path("tests/data/technique_promises.json"),
        Path("tests/data/promise_descriptions.csv"),
        Path("tests/data/conditions.csv"),
    )

    assert isinstance(technique_promises, dict)
    assert isinstance(expand_map, dict)
    assert isinstance(ok, bool)


def test_read_promise_descriptions():

    content = """promise1, Description 1
promise2, Description 2
#promise3, Description 3
# promise4, Description 4
 # promise5, Description 5"""

    promises = data.read_promise_description_file(io.StringIO(content))

    assert len(promises) == 2
    assert "promise1" in promises
    assert "promise2" in promises
