from netmiko import ConnectHandler
import getpass
import json
from datetime import datetime

# Load the JSON configuration
json_file_open = 'config.json'
with open(json_file_open, 'r') as file:
    data = json.load(file)

# Get default parameters
device_type = data['default_parameters'][0]['device_type']  
port = data['default_parameters'][0]['port']  

# Open output file to write results
with open('output.txt', 'w') as file:
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # Write current date and time to the output file
    file.write(f'Current Date and Time: {formatted_datetime}\n')
    
    # Loop through each device list in the JSON file and input the username and password for each list
    for device_list in data['lists']:  
        device_type_label = device_list['type']
        username = input(f"Username for {device_type_label}: ")
        password = getpass.getpass(f"Password for {device_type_label}: ")
        device_list['username']=username
        device_list['password']=password

    for device_list in data['lists']:  # Looping through the lists again

        for host in device_list['hosts']:  # Looping through all hosts in the list
            device_info = { 
                # fetching info for each device
                'device_type': device_type,
                'host': host,
                'port': port,
                'username': device_list['username'], 
                'password': device_list['password'],
            }

            try:
                # Establish SSH connection to the device
                net_connect = ConnectHandler(**device_info)
                print(f"\nConnected to device {host}\n")
                
                # Get the device hostname
                hostname_cmd = "show running-config | include hostname"
                hostname_output = net_connect.send_command(hostname_cmd, expect_string=r"#")
                
                # Extract hostname from the command output
                if "hostname" in hostname_output:
                    hostname = hostname_output.split("hostname")[-1].strip()
                else:
                    hostname = "Unknown"

                # Displaying the exact time the connection was established    
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                file.write(f'***************** Device: {hostname} *****************\n')
                file.write(f'Connected to device: {host} at {formatted_datetime}\n\n')

                # Execute commands from the JSON file
                for cmd in data['commands']:
                    try:
                        # Handling all possible command types with expect_string
                        response = net_connect.send_command(cmd, expect_string=r"(#|\(config.*\)#)")
                        print(f"Executing command: {cmd}\n")
                        # Write the command and its output to the file
                        file.write(f'Command: {cmd}\n\n')
                        file.write(f'Output: {response}\n\n')
                    except Exception as e:
                        print(f"Failed to execute command {cmd} on {hostname}: {e}")

                file.write(f'Disconnected from device {hostname}\n')
                file.write('-------------------------------------------------------\n\n')

            except Exception as e:
                print(f"Failed to connect to {host}: {e}")
                file.write(f"\nFailed to connect to {host}: {e}\n")
            finally:
                # Ensure the connection is closed properly
                try:
                    net_connect.disconnect()
                except:
                    pass  # If the connection was never established, we skip this

        continue  # Continue to next device list