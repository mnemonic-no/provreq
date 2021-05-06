import json

import aep.tools.libs.data as data


def test_expand_subtechniques() -> None:

    techniques = json.load(open("tests/data/technique_promises.json"))

    expanded = data.expand_techniques(techniques)

    assert len(expanded) == 349

    # Add the expanded subtechniques
    techniques.update(expanded)

    expanded, expansion_map = data.create_conditional_techniques(
        techniques)

    assert len(expanded) == 139
    assert len(expansion_map) == 525
