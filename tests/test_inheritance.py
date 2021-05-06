import pytest

import aep.tools.libs.data as data


def test_expand_techniques():

    test_techniques = {
        "T1": {
            "conditional_provides": {
                "conditional_require1": [
                    "conditional_promise1",
                    "conditional_promise2"
                ],
                "conditional_require2": [
                    "conditional_promise2"
                ]
            },
            "mitigations": [
                "mitigation1"
            ],
            "name": "Test Technique",
            "provides": [
                "promise1",
                "promise2"
            ],
            "relevant_for": [
                "testing"
            ],
            "requires": [
                "promise0"
            ],
            "subtechniques": {
                "T1.001": {
                    "name": "Threat Intel Vendors",
                    "provides": []
                },
                "T1.002": {
                    "name": "Purchase Technical Data",
                    "requires":  [
                        "promise3",
                        "promise4"
                    ]
                }
            },
            "tactic": [
                "Testing"
            ]
        }
    }

    assert len(test_techniques) == 1
    sub_tech = data.expand_techniques(test_techniques)
    test_techniques.update(sub_tech)

    assert len(test_techniques) == 3
    assert len(sub_tech) == 2

    cond_tech, cond_tech_exp_map = data.create_conditional_techniques(
        test_techniques)

    assert len(cond_tech) == 6
    assert len(cond_tech_exp_map) == 3

    test_techniques.update(cond_tech)

    assert len(test_techniques) == 9

    assert "T1" in test_techniques
    assert "T1.001" in test_techniques
    assert "T1.002" in test_techniques

    assert "T1_conditional_require1" in test_techniques
    assert "T1_conditional_require2" in test_techniques

    assert "T1.001_conditional_require1" in test_techniques
    assert "T1.001_conditional_require2" in test_techniques

    assert "T1.002_conditional_require1" in test_techniques
    assert "T1.002_conditional_require2" in test_techniques
