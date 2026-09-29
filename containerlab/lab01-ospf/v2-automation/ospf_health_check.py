from pathlib import Path

import subprocess


def check_ospf_neighbor(container, expected_neighbor, expected_state="Full"):
    command = [
        "docker",
        "exec",
        container,
        "vtysh",
        "-c",
        "show ip ospf neighbor"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    output = result.stdout
    neighbor_ok = False

    for line in output.splitlines():
        if expected_neighbor in line and expected_state in line:
            neighbor_ok = True
            break

    if neighbor_ok:
        print(
            f"{container}: Neighbor {expected_neighbor} "
            f"state {expected_state}: PASS"
        )
    else:
        print(
            f"{container}: Neighbor {expected_neighbor} "
            f"state {expected_state}: FAIL"
        )

    return neighbor_ok


def check_ospf_route(container, expected_prefix):
    command = [
        "docker",
        "exec",
        container,
        "vtysh",
        "-c",
        "show ip route ospf"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    output = result.stdout

    if expected_prefix in output:
        print(f"{container}: Route {expected_prefix}: PASS")
        return True

    print(f"{container}: Route {expected_prefix}: FAIL")
    return False

def check_ping(container, source, destination):
    command = [
        "docker",
        "exec",
        container,
        "ping",
        "-c",
        "2",
        "-W",
        "1",
        "-I",
        source,
        destination
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"{container}: Ping {source} -> {destination}: PASS")
        return True

    print(f"{container}: Ping {source} -> {destination}: FAIL")
    return False


print("=== OSPF Health Check ===")

r1_ok = check_ospf_neighbor(
    "clab-frr-ospf-r1",
    "2.2.2.2"
)

r2_ok = check_ospf_neighbor(
    "clab-frr-ospf-r2",
    "1.1.1.1"
)

r1_route_ok = check_ospf_route(
    "clab-frr-ospf-r1",
    "2.2.2.2/32"
)

r2_route_ok = check_ospf_route(
    "clab-frr-ospf-r2",
    "1.1.1.1/32"
)


r1_ping_ok = check_ping(
    "clab-frr-ospf-r1",
    "1.1.1.1",
    "2.2.2.2"
)

r2_ping_ok = check_ping(
    "clab-frr-ospf-r2",
    "2.2.2.2",
    "1.1.1.1"
)

if (
    r1_ok
    and r2_ok
    and r1_route_ok
    and r2_route_ok
    and r1_ping_ok
    and r2_ping_ok
):
    print("\nOSPF LAB STATUS: HEALTHY")
else:
    print("\nOSPF LAB STATUS: UNHEALTHY")


report_dir = Path("v2-automation/reports")
report_dir.mkdir(exist_ok=True)

status = "HEALTHY" if (
    r1_ok
    and r2_ok
    and r1_route_ok
    and r2_route_ok
    and r1_ping_ok
    and r2_ping_ok
) else "UNHEALTHY"

report = f"""OSPF HEALTH REPORT

R1 Neighbor 2.2.2.2: {"PASS" if r1_ok else "FAIL"}
R2 Neighbor 1.1.1.1: {"PASS" if r2_ok else "FAIL"}
R1 Route 2.2.2.2/32: {"PASS" if r1_route_ok else "FAIL"}
R2 Route 1.1.1.1/32: {"PASS" if r2_route_ok else "FAIL"}
R1 Ping 1.1.1.1 -> 2.2.2.2: {"PASS" if r1_ping_ok else "FAIL"}
R2 Ping 2.2.2.2 -> 1.1.1.1: {"PASS" if r2_ping_ok else "FAIL"}

OSPF LAB STATUS: {status}
"""

report_file = report_dir / "ospf_health_report.txt"
report_file.write_text(report)

print(f"\nReport saved to: {report_file}")
