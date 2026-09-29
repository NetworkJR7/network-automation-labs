from netmiko import ConnectHandler
from pathlib import Path

device = {
    "device_type": "linux",
    "host": "172.20.20.2",
    "username": "netops",
    "password": "netops123",
}

commands = {
    "ROUTING TABLE": 'vtysh -c "show ip route"',
    "OSPF": 'vtysh -c "show ip ospf"',
    "INTERFACES": 'vtysh -c "show interface brief"',
}

Path("outputs").mkdir(exist_ok=True)

conn = ConnectHandler(**device)

results = []

for title, command in commands.items():
    output = conn.send_command(command)
    section = f"\n{'=' * 15} {title} {'=' * 15}\n{output}\n"
    print(section)
    results.append(section)

conn.disconnect()

with open("outputs/r1_show_commands.txt", "w") as f:
    f.write("".join(results))

print("\nOutput guardado en outputs/r1_show_commands.txt")
