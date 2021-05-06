from typing import List, Set, Text

from pydantic import BaseModel


class AttackStage(BaseModel):
    """ Attack Stage """
    techniques: Set[Text]
    new_provides: Set[Text]
    last_stage_sum_provides: Set[Text]


class Simulation(BaseModel):
    """ Simulation result """
    stages: List[AttackStage] = []
    objectives: Set[Text] = set()
    provided: Set[Text] = set()
    backburner: List[Text] = []
    debug: List[Text] = []
