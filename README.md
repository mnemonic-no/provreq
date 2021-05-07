# Adversary Emulation Planner

This tool can be used to automatically build an ordered set of attack stages
with [MITRE ATT&CK](https://attack.mitre.org/) techniques executed during each stage.

The output is a set of attack stages that show all possible techniques that an
adversary might execute during each stage.

To decide when the different techniques are to be found in such a set, `promises` are used as access tokens for execution of techniques. Each technique defines the set of promises required to execute it (think pre-conditions) and the set of promises it provides upon execution (think post-conditions).  

## Installation

Install using pip:

```bash
pip install aep
```
You will also need to clone the [aep-data](https://github.com/mnemonic-no/aep-data) repository, which contains a starting point witch example data:

```bash
git clone https://github.com/mnemonic-no/aep-data
```

## Usage/Examples

If you have checked out the [aep-data](https://github.com/mnemonic-no/aep-data) repository you can run
these commands in that repository, since you need access to default dat files.

`aep-generate` is where you should start and the other tools are more useful if you start making changes to the
data itself.

### Generate Adversary Emulation Plan

```bash
$ aep-generate --end-condition objective_exfiltration --include-techniques T1021,T1046,T1583 --technique-bundle incident/UNC2452-Solorigate.json --show-promises
Removed 4 NOP techniques: ['T1036', 'T1036.004', 'T1036.005', 'T1083']
╒═════════╤══════════════════════════════════════════════════════════╤════════════════════════════════════════════╕
│   stage │ techniques                                               │ new promises @end-of-stage                 │
╞═════════╪══════════════════════════════════════════════════════════╪════════════════════════════════════════════╡
│       1 │ Acquire Infrastructure                                   │ exploit_available                          │
│         │ Develop Capabilities                                     │ info_domain_trust                          │
│         │ Develop Capabilities:Malware                             │ infrastructure_botnet                      │
│         │ Domain Trust Discovery                                   │ infrastructure_certificate                 │
│         │ Obtain Capabilities                                      │ infrastructure_domain                      │
│         │ Obtain Capabilities:Code Signing Certificates            │ infrastructure_server                      │
│         │ Supply Chain Compromise                                  │ privileges_user_local                      │
│         │ Supply Chain Compromise:Compromise Software Supply Chain │ tool_available                             │
│         │                                                          │ tool_delivery                              │
├─────────┼──────────────────────────────────────────────────────────┼────────────────────────────────────────────┤
│       2 │ Command and Scripting Interpreter                        │ access_filesystem                          │
│         │ Command and Scripting Interpreter:PowerShell             │ code_executed                              │
│         │ Command and Scripting Interpreter:Windows Command Shell  │ defense_evasion                            │
│         │ Scheduled Task/Job                                       │ file_transfer                              │
│         │                                                          │ persistence                                │
├─────────┼──────────────────────────────────────────────────────────┼────────────────────────────────────────────┤
│       3 │ Account Discovery                                        │ access_network                             │
│         │ Application Layer Protocol                               │ adversary_controlled_communication_channel │
│         │ Application Layer Protocol:Web Protocols                 │ credentials_user_domain                    │
│         │ Obfuscated Files or Information [*]                      │ credentials_user_local                     │
│         │ Permission Groups Discovery                              │ credentials_user_thirdparty                │
│         │ Process Discovery                                        │ info_groupname                             │
│         │ Signed Binary Proxy Execution [*]                        │ info_process_info                          │
│         │ Signed Binary Proxy Execution:Rundll32 [*]               │ info_target_employee                       │
│         │ Unsecured Credentials                                    │ info_username                              │
│         │ Unsecured Credentials:Private Keys                       │                                            │
├─────────┼──────────────────────────────────────────────────────────┼────────────────────────────────────────────┤
│       4 │ Account Manipulation:Additional Cloud Credentials [*]    │ info_cloud_services                        │
│         │ Cloud Service Discovery                                  │ info_email_address                         │
│         │ Dynamic Resolution [*]                                   │ info_network_hosts                         │
│         │ Dynamic Resolution:Domain Generation Algorithms [*]      │ info_network_services                      │
│         │ Email Collection                                         │ privileges_system_local                    │
│         │ Email Collection:Remote Email Collection                 │                                            │
│         │ Event Triggered Execution                                │                                            │
│         │ Ingress Tool Transfer [*]                                │                                            │
│         │ Network Service Scanning                                 │                                            │
│         │ Valid Accounts [*]                                       │                                            │
╘═════════╧══════════════════════════════════════════════════════════╧════════════════════════════════════════════╛
[*] Technique does not provide any new promises
FAIL: incomplete attack chain, could not achieve end condition: objective_exfiltration
```

### Show Promise Usage

Show little or unused promises.

```bash
aep-promise-usage
╒══════════════════════════════════════╤════════════╤════════════╕
│ promise                              │   provides │   requires │
╞══════════════════════════════════════╪════════════╪════════════╡
│ info_cloud_hosts                     │          8 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ objective_denial_of_service          │         11 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ privileges_users                     │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ staged_data                          │          7 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ fast_flux                            │          0 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ info_network_config                  │          7 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ waterhole                            │          0 │          2 │
├──────────────────────────────────────┼────────────┼────────────┤
│ info_password_policy                 │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ objective_integrity                  │          8 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ info_domain_trust                    │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ infrastructure_trusted_social_media  │          6 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ info_system_time                     │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ credentials_2fa_token                │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ infrastructure_domain                │         14 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ objective_exfiltration               │         15 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ info_cloud_services                  │          8 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ objective_destruction                │         11 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ infrastructure_certificate           │         12 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ access_network_intercept             │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ infrastructure_trusted_email_account │          6 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ objective_resources_computational    │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ objective_extortion                  │          4 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ persistence                          │        164 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ info_target_information              │          1 │          0 │
├──────────────────────────────────────┼────────────┼────────────┤
│ defense_evasion                      │         97 │          0 │
╘══════════════════════════════════════╧════════════╧════════════╛
```

### Show Techniques

Show summary based on MITRE ATT&CK technique ID.

```bash
aep-technique -t T1001
+++
        Data Obfuscation
╒═════════════════╤════════════════╤═════════════════════╤══════════════════════════════╤════════════════╤════════════════════════╕
│ Provides        │ Requires       │ Tactic(s)           │ Relevant                     │ Conditionals   │ Subtechniques          │
╞═════════════════╪════════════════╪═════════════════════╪══════════════════════════════╪════════════════╪════════════════════════╡
│ defense_evasion │ code_executed  │ Command and Control │ authentication_server        │                │ Junk Data              │
│                 │ tool_available │                     │ backup_server                │                │ Steganography          │
│                 │ tool_delivery  │                     │ client                       │                │ Protocol Impersonation │
│                 │                │                     │ content_management_server    │                │                        │
│                 │                │                     │ database_server              │                │                        │
│                 │                │                     │ directory_server             │                │                        │
│                 │                │                     │ file_server                  │                │                        │
│                 │                │                     │ instant_messaging_server     │                │                        │
│                 │                │                     │ log_server                   │                │                        │
│                 │                │                     │ login_server                 │                │                        │
│                 │                │                     │ mail_server                  │                │                        │
│                 │                │                     │ name_server                  │                │                        │
│                 │                │                     │ network_firewall             │                │                        │
│                 │                │                     │ network_management_server    │                │                        │
│                 │                │                     │ network_router               │                │                        │
│                 │                │                     │ print_server                 │                │                        │
│                 │                │                     │ proxy_server                 │                │                        │
│                 │                │                     │ software_distribution_server │                │                        │
│                 │                │                     │ virtualization_server        │                │                        │
│                 │                │                     │ web_server                   │                │                        │
╘═════════════════╧════════════════╧═════════════════════╧══════════════════════════════╧════════════════╧════════════════════════╛
```

### Technique bundle summary

```bash
aep-bundle -b incident/Ryuk-Bazar-Cobalt-Strike.json

(...)
```

### Promise summary

```bash
aep-promise --promise tool_delivery

(...)
```

### Search promises

Search promises based on specified criterias.

```bash
aep-promise-search --help
usage: aep-promise-search [-h] [--config-dir CONFIG_DIR] [--data-dir DATA_DIR]
                          [--promise-descriptions PROMISE_DESCRIPTIONS]
                          [--conditions CONDITIONS]
                          [--technique-promises TECHNIQUE_PROMISES]
                          [-p PROVIDES] [-np NOTPROVIDES] [-r REQUIRES]
                          [-nr NOTREQUIRES] [-n NAME]

Search techniques

optional arguments:
  -h, --help            show this help message and exit
  --config-dir CONFIG_DIR
                        Default config dir with configurations for scio and
                        plugins
  --data-dir DATA_DIR   Root directory of data files
  --promise-descriptions PROMISE_DESCRIPTIONS
                        Promise description file (CSV)
  --conditions CONDITIONS
                        Conditions (CSV)
  --technique-promises TECHNIQUE_PROMISES
                        Path for techniques.json. Supports data relative to
                        root data directory and absolute path
  -p PROVIDES, --provides PROVIDES
                        Search for techniques providing these promises
  -np NOTPROVIDES, --notprovides NOTPROVIDES
                        Search for techniques that does _not_ provide promises
  -r REQUIRES, --requires REQUIRES
                        Search for techniques requires these promises
  -nr NOTREQUIRES, --notrequires NOTREQUIRES
                        Search for techniques that does _not_ require promises
  -n NAME, --name NAME  Search for techniques whos name contains this string
```


## Configuration

This step is not necessary, but can be used to change default settings on the tools. Run with:

```bash
aep-config user
```

which will create default settings in ~/.config/aep/config.

## About

The Adversary Emulation Planner is developed in the SOCCRATES innovation project (<https://soccrates.eu>). SOCCRATES has received funding from the European Union’s Horizon 2020 Research and Innovation program under Grant Agreement No. 833481.
