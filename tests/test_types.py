import pydantic
import pytest

import provreq.tools.libs.types as types


def test_types() -> None:

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        attack_stage = types.AttackStage()

    attack_stage = types.AttackStage(
        agents=[], new_provides=[], last_stage_sum_provides=[])

    assert hasattr(attack_stage, "agents")
    assert hasattr(attack_stage, "new_provides")
    assert hasattr(attack_stage, "last_stage_sum_provides")

    try:
        simulation = types.Simulation()
    except Exception as exception:
        raise pytest.fail(f"DID RAISE {exception}")

    simulation = types.Simulation(
        stages=[], objectives=[], provided=[], backburner=[], debug=[])

    assert hasattr(simulation, "stages")
    assert hasattr(simulation, "objectives")
    assert hasattr(simulation, "provided")
    assert hasattr(simulation, "backburner")
    assert hasattr(simulation, "debug")
