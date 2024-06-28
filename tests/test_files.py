"""Test for generate.py"""

import io
from pathlib import Path

import provreq.tools.libs.data as data


def test_read_files() -> None:

    agent_promises, expand_map, ok = data.read_agent_promises(
        Path("tests/data/agent_promises.json"),
        Path("tests/data/promise_descriptions.csv"),
        Path("tests/data/conditions.csv"),
    )

    assert isinstance(agent_promises, dict)
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
