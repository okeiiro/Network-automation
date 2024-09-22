from netmiko import ConnectHandler
import getpass
import json

# Load JSON configuration
json_file_open = 'vpn_config.json'

with open(json_file_open, 'r') as file:
    data = json.load(file)

device_type = data['default_parameters'][0]['device_type']
port = data['default_parameters'][0]['port']

# Using new key from the config file
newkey = data['keys'][0]['new_key']
print("New key: ", newkey)

# Get username and password from user input
username = input("Username: ")
password = getpass.getpass("Password: ")

# Regular expression for handling different prompts
expect_prompt = r"(#|\(config.*\)#)"

# Loop through the hosts and establish connection
for host in data['hosts']:
    device_info = {
        'device_type': device_type,
        'host': host,
        'port': port,
        'username': username,
        'password': password,
    }

    try:
        # Establish SSH connection to the device
        net_connect = ConnectHandler(**device_info)
        print(f"\n\nConnected to device {host}")
    except Exception as e:
        print(f"Failed to connect to device {host}: {e}")
        continue  # Skip to the next host if connection fails

    try:
        # Get the device hostname
        hostname_output = net_connect.send_command("show running-config | include hostname", expect_string=expect_prompt)
        hostname = hostname_output.split()[1]
        print(f"Setting new key for {hostname}:\n")  # Get device hostname

        # Get the old VPN key
        oldkey_output = net_connect.send_command("show running-config | include crypto isakmp key", expect_string=expect_prompt)
        oldkey = oldkey_output.split()[3]
        print(f"Old key: {oldkey}")  # Get VPN old key

        # Enter configuration mode
        net_connect.send_command("conf t", expect_string=r"\(config\)#")
        print("Entered configuration mode\n")

        # Remove old key and add the new key
        net_connect.send_command(f"no crypto isakmp key {oldkey} address 0.0.0.0 0.0.0.0", expect_string=r"\(config\)#")
        net_connect.send_command(f"crypto isakmp key {newkey} address 0.0.0.0 0.0.0.0", expect_string=r"\(config\)#")
        print(f"Old key removed and new key {newkey} added")

        # Exit configuration mode
        net_connect.send_command("exit", expect_string=expect_prompt)
        # Save the configuration
        #net_connect.save_config()
        net_connect.send_command("write memory", expect_string=expect_prompt)

        print("Configuration saved\n")

        # Verify the new key
        output = net_connect.send_command("show running-config | include crypto isakmp key", expect_string=expect_prompt)
        print(f"New key verification output:\n{output}")

    except Exception as e:
        print(f"Failed to execute commands on {host}: {e}")
    finally:
        # Disconnect from the device
        net_connect.disconnect()
        print(f"Disconnected from device {host}")
