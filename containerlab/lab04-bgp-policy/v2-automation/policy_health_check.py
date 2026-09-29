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

            session_ok = state.isdigit()
            as_ok = remote_as == str(expected_as)

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

def check_policy(
    container,
    prefix,
    preferred_next_hop,
    preferred_as,
    expected_localpref,
    backup_next_hop,
    backup_as
):
    output = run_vtysh(
        container,
        f"show bgp ipv4 unicast {prefix}"
    )

    paths = {}
    current_as = None
    current_next_hop = None

    for line in output.splitlines():
        stripped = line.strip()

        # AS path line such as "65002" or "65003"
        if stripped.isdigit():
            current_as = stripped
            current_next_hop = None
            continue

        # Next-hop line
        if current_as and " from " in stripped:
            current_next_hop = stripped.split()[0]

            paths[current_next_hop] = {
                "as": current_as,
                "localpref": 100,
                "best": False
            }

            continue

        # Attributes belonging to the current path
        if current_next_hop and "Origin" in stripped:
            if "localpref" in stripped:
                parts = stripped.replace(",", "").split()

                if "localpref" in parts:
                    index = parts.index("localpref")
                    paths[current_next_hop]["localpref"] = int(
                        parts[index + 1]
                    )

            if "best" in stripped:
                paths[current_next_hop]["best"] = True

    preferred = paths.get(preferred_next_hop)
    backup = paths.get(backup_next_hop)

    preferred_ok = (
        preferred is not None
        and preferred["as"] == str(preferred_as)
        and preferred["localpref"] == expected_localpref
        and preferred["best"] is True
    )

    backup_ok = (
        backup is not None
        and backup["as"] == str(backup_as)
        and backup["best"] is False
    )

    if preferred_ok and backup_ok:
        print(
            f"{container}: BGP policy for {prefix}: PASS"
        )
        return True

    print(
        f"{container}: BGP policy for {prefix}: FAIL"
    )

    if preferred:
        print(
            f"  Expected best via {preferred_next_hop} "
            f"LP {expected_localpref} | "
            f"Actual LP {preferred['localpref']} "
            f"Best={preferred['best']}"
        )

    if backup:
        print(
            f"  Backup via {backup_next_hop} "
            f"Best={backup['best']}"
        )

    return False


def check_rib_next_hop(
    container,
    prefix,
    expected_next_hop
):
    output = run_vtysh(
        container,
        "show ip route bgp"
    )

    for line in output.splitlines():
        if prefix in line:
            route_ok = (
                expected_next_hop in line
                and line.startswith("B>*")
            )

            if route_ok:
                print(
                    f"{container}: RIB {prefix} "
                    f"via {expected_next_hop}: PASS"
                )
                return True

    print(
        f"{container}: RIB {prefix} "
        f"via {expected_next_hop}: FAIL"
    )
    return False


print("=== BGP Policy Health Check ===")

r1_r2_session_ok = check_bgp_session(
    "clab-frr-bgp-policy-r1",
    "10.40.12.2",
    65002
)

r1_r3_session_ok = check_bgp_session(
    "clab-frr-bgp-policy-r1",
    "10.40.13.2",
    65003
)

policy_ok = check_policy(
    "clab-frr-bgp-policy-r1",
    "203.0.113.0/24",
    "10.40.12.2",
    65002,
    200,
    "10.40.13.2",
    65003
)

rib_ok = check_rib_next_hop(
    "clab-frr-bgp-policy-r1",
    "203.0.113.0/24",
    "10.40.12.2"
)

if (
    r1_r2_session_ok
    and r1_r3_session_ok
    and policy_ok
    and rib_ok
):
    print("\nBGP POLICY LAB STATUS: HEALTHY")
else:
    print("\nBGP POLICY LAB STATUS: UNHEALTHY")
status = "HEALTHY" if (
    r1_r2_session_ok
    and r1_r3_session_ok
    and policy_ok
    and rib_ok
) else "UNHEALTHY"

report_dir = Path("v2-automation/reports")
report_dir.mkdir(exist_ok=True)

report = f"""BGP POLICY HEALTH REPORT

R1 -> R2 Session: {"PASS" if r1_r2_session_ok else "FAIL"}
R1 -> R3 Session: {"PASS" if r1_r3_session_ok else "FAIL"}

Policy 203.0.113.0/24 via R2 LocalPref 200: {"PASS" if policy_ok else "FAIL"}
RIB 203.0.113.0/24 via 10.40.12.2: {"PASS" if rib_ok else "FAIL"}

BGP POLICY LAB STATUS: {status}
"""

report_file = report_dir / "policy_health_report.txt"
report_file.write_text(report)

print(f"\nReport saved to: {report_file}")
