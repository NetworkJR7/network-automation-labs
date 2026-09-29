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


def check_bgp_session(container, neighbor, expected_as):
    output = run_vtysh(
        container,
        "show bgp summary"
    )

    for line in output.splitlines():

        if neighbor in line:
            columns = line.split()

            remote_as = columns[2]
            state = columns[9]

            as_ok = remote_as == str(expected_as)

            # If State/PfxRcd contains a number,
            # the BGP session is established.
            session_ok = state.isdigit()

            if session_ok and as_ok:
                print(
                    f"{container}: Neighbor {neighbor} "
                    f"AS{expected_as}: PASS"
                )
                return True

            print(
                f"{container}: Neighbor {neighbor} "
                f"AS{expected_as}: FAIL"
            )
            return False

    print(
        f"{container}: Neighbor {neighbor}: NOT FOUND"
    )

    return False

def check_bgp_prefix(container, expected_prefix, expected_as):
    output = run_vtysh(
        container,
        "show bgp ipv4 unicast"
    )

    for line in output.splitlines():
        if expected_prefix in line:
            line_ok = line.strip().startswith("*>")
            as_ok = str(expected_as) in line

            if line_ok and as_ok:
                print(
                    f"{container}: Prefix {expected_prefix} "
                    f"via AS{expected_as}: PASS"
                )
                return True

            print(
                f"{container}: Prefix {expected_prefix} "
                f"via AS{expected_as}: FAIL"
            )
            return False

    print(
        f"{container}: Prefix {expected_prefix}: NOT FOUND"
    )
    return False

def check_bgp_rib(container, expected_prefix):
    output = run_vtysh(
        container,
        "show ip route bgp"
    )

    for line in output.splitlines():
        if expected_prefix in line:
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

print("=== eBGP Health Check ===")

r1_session_ok = check_bgp_session(
    "clab-frr-ebgp-r1",
    "10.20.12.2",
    65002
)

r2_session_ok = check_bgp_session(
    "clab-frr-ebgp-r2",
    "10.20.12.1",
    65001
)

r1_prefix_ok = check_bgp_prefix(
    "clab-frr-ebgp-r1",
    "2.2.2.2/32",
    65002
)

r2_prefix_ok = check_bgp_prefix(
    "clab-frr-ebgp-r2",
    "1.1.1.1/32",
    65001
)

r1_rib_ok = check_bgp_rib(
    "clab-frr-ebgp-r1",
    "2.2.2.2/32"
)

r2_rib_ok = check_bgp_rib(
    "clab-frr-ebgp-r2",
    "1.1.1.1/32"
)

r1_ping_ok = check_ping(
    "clab-frr-ebgp-r1",
    "1.1.1.1",
    "2.2.2.2"
)

r2_ping_ok = check_ping(
    "clab-frr-ebgp-r2",
    "2.2.2.2",
    "1.1.1.1"
)


if (
    r1_session_ok
    and r2_session_ok
    and r1_prefix_ok
    and r2_prefix_ok
    and r1_rib_ok
    and r2_rib_ok
    and r1_ping_ok
    and r2_ping_ok
):
    print("\neBGP LAB STATUS: HEALTHY")
else:
    print("\neBGP LAB STATUS: UNHEALTHY")
status = "HEALTHY" if (
    r1_session_ok
    and r2_session_ok
    and r1_prefix_ok
    and r2_prefix_ok
    and r1_rib_ok
    and r2_rib_ok
    and r1_ping_ok
    and r2_ping_ok
) else "UNHEALTHY"

report_dir = Path("v2-automation/reports")
report_dir.mkdir(exist_ok=True)

report = f"""eBGP HEALTH REPORT

R1 Neighbor 10.20.12.2 AS65002: {"PASS" if r1_session_ok else "FAIL"}
R2 Neighbor 10.20.12.1 AS65001: {"PASS" if r2_session_ok else "FAIL"}

R1 Prefix 2.2.2.2/32 via AS65002: {"PASS" if r1_prefix_ok else "FAIL"}
R2 Prefix 1.1.1.1/32 via AS65001: {"PASS" if r2_prefix_ok else "FAIL"}

R1 RIB Route 2.2.2.2/32: {"PASS" if r1_rib_ok else "FAIL"}
R2 RIB Route 1.1.1.1/32: {"PASS" if r2_rib_ok else "FAIL"}

R1 Ping 1.1.1.1 -> 2.2.2.2: {"PASS" if r1_ping_ok else "FAIL"}
R2 Ping 2.2.2.2 -> 1.1.1.1: {"PASS" if r2_ping_ok else "FAIL"}

eBGP LAB STATUS: {status}
"""

report_file = report_dir / "bgp_health_report.txt"
report_file.write_text(report)

print(f"\nReport saved to: {report_file}")
