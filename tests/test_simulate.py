from pathlib import Path

import provreq.tools.libs.data as data
import provreq.tools.libs.libgenerate as libgenerate
import provreq.tools.libs.types as types


def test_simulate() -> None:
    agents = data.read_agent_bundle(Path("tests/data/agent_bundle.json"))

    agent_promises, expand_map, _ = data.read_agent_promises(
        Path("tests/data/agent_promises.json"),
        Path("tests/data/promise_descriptions.csv"),
        Path("tests/data/conditions.csv"),
    )

    agents = data.preprocess_agents(
        agent_promises,
        expand_map,
        agents)

    agents += ["T1046", "T1583"]

    sim = libgenerate.simulate([], agents, agent_promises, [])

    target_sim = libgenerate.Simulation(stages=[types.AttackStage(agents={'T1588.003', 'T1083', 'T1588', 'T1482', 'T1583', 'T1036', 'T1036.005', 'T1195', 'T1587', 'T1587.001', 'T1036.004', 'T1195.002'}, new_provides={'infrastructure_server', 'info_domain_trust', 'tool_delivery', 'infrastructure_domain', 'privileges_user_local', 'exploit_available', 'tool_available', 'infrastructure_certificate', 'defense_evasion', 'infrastructure_botnet'}, last_stage_sum_provides=set()), types.AttackStage(agents={'T1059', 'T1053', 'T1059.003', 'T1059.001'}, new_provides={'code_executed', 'persistence', 'file_transfer'}, last_stage_sum_provides={'infrastructure_server', 'info_domain_trust', 'tool_delivery', 'infrastructure_domain', 'privileges_user_local', 'exploit_available', 'tool_available', 'infrastructure_certificate', 'defense_evasion', 'infrastructure_botnet'}), types.AttackStage(agents={'T1069', 'T1087', 'T1057', 'T1218', 'T1027', 'T1071', 'T1218.011', 'T1071.001'}, new_provides={'access_network', 'adversary_controlled_communication_channel', 'info_username', 'info_process_info', 'info_target_employee', 'info_groupname'}, last_stage_sum_provides={'infrastructure_server', 'info_domain_trust', 'tool_delivery', 'infrastructure_domain', 'code_executed', 'persistence', 'privileges_user_local', 'exploit_available', 'tool_available', 'infrastructure_certificate', 'file_transfer', 'defense_evasion', 'infrastructure_botnet'}), types.AttackStage(agents={'T1568', 'T1546', 'T1568.002', 'T1046', 'T1105'}, new_provides={'info_network_services', 'privileges_system_local', 'info_network_hosts'}, last_stage_sum_provides={
        'tool_delivery', 'info_username', 'infrastructure_certificate', 'tool_available', 'file_transfer', 'info_groupname', 'infrastructure_botnet', 'code_executed', 'privileges_user_local', 'exploit_available', 'info_target_employee', 'access_network', 'adversary_controlled_communication_channel', 'info_process_info', 'defense_evasion', 'infrastructure_server', 'info_domain_trust', 'infrastructure_domain', 'persistence'})], objectives=set(),  provided={'tool_delivery', 'access_network', 'adversary_controlled_communication_channel', 'privileges_system_local', 'info_network_hosts', 'info_username', 'infrastructure_certificate', 'tool_available', 'info_process_info', 'file_transfer', 'info_groupname', 'defense_evasion', 'infrastructure_botnet', 'infrastructure_server', 'info_domain_trust', 'infrastructure_domain', 'code_executed', 'persistence', 'privileges_user_local', 'exploit_available', 'info_target_employee', 'info_network_services'}, backburner=['T1553.002', 'T1070.004', 'T1070', 'T1567', 'T1098.002', 'T1114', 'T1003.006', 'T1560.001', 'T1069.002', 'T1098', 'T1078', 'T1053.005', 'T1553', 'T1074', 'T1560', 'T1552.004', 'T1098.001', 'T1526', 'T1005', 'T1552', 'T1003', 'T1114.002', 'T1546.003', 'T1074.002', 'T1190', 'T1546_privileges_admin_local', 'T1114_moved_laterally', 'T1003.006_poor_security_practices', 'T1083_moved_laterally', 'T1078_previous_compromise', 'T1053.005_poor_security_practices', 'T1053_poor_security_practices', 'T1552.004_poor_security_practices', 'T1552_poor_security_practices', 'T1003_poor_security_practices', 'T1114.002_moved_laterally', 'T1546.003_privileges_admin_local', 'T1190_poor_security_practices'], debug=[])

    assert sim is not None

    assert target_sim.provided == sim.provided
    assert set(target_sim.backburner) == set(sim.backburner)
    for i, stage in enumerate(target_sim.stages):
        assert stage.agents == sim.stages[i].agents
        assert stage.new_provides == sim.stages[i].new_provides
