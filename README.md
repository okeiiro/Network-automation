# Network automation project
Python scripts to automate networking tasks

## Pre-requisites
Ensure you have the following installed:

- Python 3.x
- Netmiko library

You can install Netmiko using pip:

```bash
pip install netmiko
```

## send_commands.py
Python script to automate router/switch commands with authentification handling.
You can add your commands in the config.json file inside commandes folder

```bash
    "commands": [
        "sh run | include hostname",
        "conf t",
        "interface g0/0",
        "exit",
        "exit",
        "show version",
        "write memory"
    ]
```

## vpn_key.py
Python script to automatically update vpn keys accross different routers with authentification handling.
You can add the new vpn key in the vpn_config.json file inside vpn folder

```bash
    "keys": [
        {
            "new_key": "hblVZBHLV<S:u00f9fn"
        }
    ]
```
