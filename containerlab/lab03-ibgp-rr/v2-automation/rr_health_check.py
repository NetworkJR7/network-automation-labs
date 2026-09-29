from pathlib import Path

import subprocess


def run_vtysh(container, command):
    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "vtysh",
            "-c",
            command
        ],
        capture_output=True,
        text=True
    )

    return result.stdout


def check_bgp_session(container, neighbor):
    output = run_vtysh(
        container,
        "show bgp summary"
    )

    for line in output.splitlines():
        if neighbor in line:
            columns = line.split()

            state = columns[9]

            if state.isdigit():
                print(
                    f"{container}: BGP neighbor {neighbor}: PASS"
                )
                return True

            print(
                f"{container}: BGP neighbor {neighbor}: FAIL"
            )
            return False

    print(
        f"{container}: BGP neighbor {neighbor}: NOT FOUND"
    )

    return False


def check_reflected_route(
    container,
    prefix,
    expected_next_hop,
    expected_originator,
    expected_cluster
):
    output = run_vtysh(
        container,
        f"show bgp ipv4 unicast {prefix}"
    )

    prefix_ok = prefix in output
    best_ok = "best" in output
    next_hop_ok = expected_next_hop in output

    originator_ok = (
        f"Originator: {expected_originator}" in output
    )

    cluster_ok = (
        f"Cluster list: {expected_cluster}" in output
    )

    result = (
        prefix_ok
        and best_ok
        and next_hop_ok
        and originator_ok
        and cluster_ok
    )

    if result:
        print(
            f"{container}: Reflected route {prefix}: PASS"
        )
    else:
        print(
            f"{container}: Reflected route {prefix}: FAIL"
        )

    return result

def check_bgp_rib(container, expected_prefix):
    output = run_vtysh(
        container,
        "show ip route bgp"
    )

    if expected_prefix in output:
        print(
            f"{container}: RIB route {expected_prefix}: PASS"
        )
        return True

    print(
        f"{container}: RIB route {expected_prefix}: FAIL"
    )
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
        print(
            f"{container}: Ping {source} -> {destination}: PASS"
        )
        return True

    print(
        f"{container}: Ping {source} -> {destination}: FAIL"
    )
    return False

print("=== iBGP Route Reflector Health Check ===")

r1_session_ok = check_bgp_session(
    "clab-frr-ibgp-rr-r1",
    "10.30.12.2"
)

r3_session_ok = check_bgp_session(
    "clab-frr-ibgp-rr-r3",
    "10.30.23.1"
)

r1_route_ok = check_reflected_route(
    "clab-frr-ibgp-rr-r1",
    "3.3.3.3/32",
    "10.30.12.2",
    "3.3.3.3",
    "2.2.2.2"
)

r3_route_ok = check_reflected_route(
    "clab-frr-ibgp-rr-r3",
    "1.1.1.1/32",
    "10.30.23.1",
    "1.1.1.1",
    "2.2.2.2"
)

r1_rib_ok = check_bgp_rib(
    "clab-frr-ibgp-rr-r1",
    "3.3.3.3/32"
)

r3_rib_ok = check_bgp_rib(
    "clab-frr-ibgp-rr-r3",
    "1.1.1.1/32"
)

r1_ping_ok = check_ping(
    "clab-frr-ibgp-rr-r1",
    "1.1.1.1",
    "3.3.3.3"
)

r3_ping_ok = check_ping(
    "clab-frr-ibgp-rr-r3",
    "3.3.3.3",
    "1.1.1.1"
)

if (
    r1_session_ok
    and r3_session_ok
    and r1_route_ok
    and r3_route_ok
    and r1_rib_ok
    and r3_rib_ok
    and r1_ping_ok
    and r3_ping_ok
):
    print("\niBGP RR LAB STATUS: HEALTHY")
else:
    print("\niBGP RR LAB STATUS: UNHEALTHY")

status = "HEALTHY" if (
    r1_session_ok
    and r3_session_ok
    and r1_route_ok
    and r3_route_ok
    and r1_rib_ok
    and r3_rib_ok
    and r1_ping_ok
    and r3_ping_ok
) else "UNHEALTHY"

report_dir = Path("v2-automation/reports")
report_dir.mkdir(exist_ok=True)

report = f"""iBGP ROUTE REFLECTOR HEALTH REPORT

R1 -> RR Session: {"PASS" if r1_session_ok else "FAIL"}
R3 -> RR Session: {"PASS" if r3_session_ok else "FAIL"}

R1 Reflected Route 3.3.3.3/32: {"PASS" if r1_route_ok else "FAIL"}
R3 Reflected Route 1.1.1.1/32: {"PASS" if r3_route_ok else "FAIL"}

R1 RIB Route 3.3.3.3/32: {"PASS" if r1_rib_ok else "FAIL"}
R3 RIB Route 1.1.1.1/32: {"PASS" if r3_rib_ok else "FAIL"}

R1 Ping 1.1.1.1 -> 3.3.3.3: {"PASS" if r1_ping_ok else "FAIL"}
R3 Ping 3.3.3.3 -> 1.1.1.1: {"PASS" if r3_ping_ok else "FAIL"}

iBGP RR LAB STATUS: {status}
"""

report_file = report_dir / "rr_health_report.txt"
report_file.write_text(report)

print(f"\nReport saved to: {report_file}")
