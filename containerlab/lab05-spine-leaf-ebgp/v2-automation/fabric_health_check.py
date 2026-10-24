#!/usr/bin/env python3
"""Data-driven FRRouting Spine-Leaf underlay validation (Docker transport)."""
import argparse
import ipaddress
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


def run(container, *command):
    result = subprocess.run(
        ["docker", "exec", container, *command],
        capture_output=True, text=True, timeout=15, check=False,
    )
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or "command failed")
    return result.stdout


def frr(container, command):
    return run(container, "vtysh", "-c", command)


def bgp_summary(output):
    local = re.search(r"local AS number\s+(\d+)", output)
    if not local:
        raise ValueError("Cannot parse local AS from BGP summary")
    peers = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 10:
            continue
        try:
            ipaddress.ip_address(fields[0])
            remote_as = int(fields[2])
        except (ValueError, IndexError):
            continue
        # With established sessions FRR prints numeric PfxRcd; (Policy) indicates established but filtered.
        peers[fields[0]] = {"remote_as": remote_as, "established": fields[9].isdigit(),
                            "received_prefixes": int(fields[9]) if fields[9].isdigit() else None,
                            "state": fields[9]}
    return int(local.group(1)), peers


def rib_entry(output):
    match = re.search(r'Known via\s+"([^"]+)"', output)
    protocol = match.group(1) if match else None
    nexthops = re.findall(r"^\s*\*\s+([0-9.]+),\s+via\s+(\S+)", output, re.M)
    return protocol, [ip for ip, _ in nexthops]


def kernel_entry(output):
    routes = json.loads(output)
    if not routes:
        return None, []
    route = routes[0]
    if "nexthops" in route:
        return route.get("protocol"), [n.get("gateway") for n in route["nexthops"]]
    gateway = route.get("gateway")
    return route.get("protocol"), [gateway] if gateway else []


def check(result, name, ok, observed):
    result["checks"].append({"name": name, "passed": bool(ok), "observed": observed})


def validate_node(name, node, expected):
    result = {"node": name, "checks": [], "status": "HEALTHY"}
    container = node["container"]
    try:
        local_as, neighbors = bgp_summary(frr(container, "show bgp ipv4 unicast summary"))
        check(result, "local_as", local_as == int(expected["local_as"]), local_as)
        for address, asn in expected["neighbors"].items():
            addr = str(address)
            peer = neighbors.get(addr)
            check(result, f"neighbor:{addr}:established", bool(peer and peer["established"]),
                  peer["state"] if peer else "MISSING")
            check(result, f"neighbor:{addr}:remote_as", bool(peer and peer["remote_as"] == int(asn)),
                  peer["remote_as"] if peer else "MISSING")
        configured = len(neighbors)
        expected_count = len(expected["neighbors"])
        established = sum(
            bool(neighbors.get(str(ip), {}).get("established"))
            for ip in expected["neighbors"]
        )

        check(result, "neighbor_configured_count",
              configured == expected_count,
              f"{configured}/{expected_count}")

        check(result, "neighbor_established_count",
              established == expected_count,
              f"{established}/{expected_count}")

        # Interface Health Validation
        expected_interfaces = expected.get("interfaces", {})
        if expected_interfaces:
            links = {
                item["ifname"]: item
                for item in json.loads(
                    run(container, "ip", "-j", "link", "show")
                )
            }

            addresses = {
                item["ifname"]: item
                for item in json.loads(
                    run(container, "ip", "-j", "-4", "addr", "show")
                )
            }

            for interface, config in expected_interfaces.items():
                link = links.get(interface)
                addr = addresses.get(interface, {})

                if link is None:
                    check(result, f"interface:{interface}",
                          False, "MISSING")
                    continue

                flags = link.get("flags", [])
                admin_up = "UP" in flags
                oper_up = (
                    link.get("operstate") == "UP"
                    or "LOWER_UP" in flags
                )

                actual_ips = {
                    f"{ip['local']}/{ip['prefixlen']}"
                    for ip in addr.get("addr_info", [])
                }

                expected_ip = config.get("address")

                ok = (
                    admin_up
                    and oper_up
                    and (not expected_ip or expected_ip in actual_ips)
                )

                check(result, f"interface:{interface}", ok, {
                    "admin_up": admin_up,
                    "oper_up": oper_up,
                    "addresses": sorted(actual_ips),
                    "expected_address": expected_ip,
                })

        lo = json.loads(run(container, "ip", "-j", "-4", "addr", "show", "lo"))
        actual_lo = {f"{addr['local']}/{addr['prefixlen']}" for iface in lo
                     for addr in iface.get("addr_info", [])}
        check(result, "loopback", expected["loopback"] in actual_lo, sorted(actual_lo))

        bgp_table = frr(container, "show bgp ipv4 unicast")
        for prefix, spec in expected.get("routes", {}).items():
            # BGP table rows begin with a status symbol and the prefix.
            has_bgp = bool(re.search(r"^\s*[\*sdhSrR>=i]+\s+" + re.escape(prefix) + r"\s", bgp_table, re.M))
            check(result, f"bgp:{prefix}", has_bgp, "PRESENT" if has_bgp else "MISSING")

            proto, rib_hops = rib_entry(frr(container, f"show ip route {prefix}"))
            expected_hops = int(spec["nexthops"])
            required = set(spec.get("via", []))
            rib_ok = proto == spec["protocol"] and len(rib_hops) == expected_hops and (not required or set(rib_hops) == required)
            check(result, f"rib:{prefix}", rib_ok,
                  {"protocol": proto, "nexthops": rib_hops, "expected": expected_hops})

            kernel_proto, kernel_hops = kernel_entry(run(container, "ip", "-j", "-4", "route", "show", prefix))
            fib_ok = kernel_proto == spec["protocol"] and len(kernel_hops) == expected_hops and (not required or set(kernel_hops) == required)
            check(result, f"fib:{prefix}", fib_ok,
                  {"protocol": kernel_proto, "nexthops": kernel_hops, "expected": expected_hops})
            # RIB-Kernel Consistency Validation
            rib_set = set(rib_hops)
            kernel_set = set(kernel_hops)

            consistency_ok = (
                proto == kernel_proto
                and rib_set == kernel_set
            )

            check(
                result,
                f"rib_kernel_consistency:{prefix}",
                consistency_ok,
                {
                    "rib_only": sorted(rib_set - kernel_set),
                    "kernel_only": sorted(kernel_set - rib_set),
                    "rib_protocol": proto,
                    "kernel_protocol": kernel_proto,
                },
            )

    except (RuntimeError, subprocess.TimeoutExpired, ValueError, KeyError, json.JSONDecodeError) as exc:
        check(result, "collection", False, f"{type(exc).__name__}: {exc}")
        result["status"] = "DOWN"
        return result

    failures = [
        item for item in result["checks"]
        if not item["passed"]
    ]

    if failures:
        critical = (
            established == 0 and expected_count > 0
        ) or (
            any(
                item["name"].startswith("interface:")
                and item["observed"] == "MISSING"
                for item in failures
            )
        )

        result["status"] = "DOWN" if critical else "DEGRADED"

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent
    parser.add_argument("--inventory", type=Path, default=base / "inventory.yaml")
    parser.add_argument("--expected", type=Path, default=base / "expected_state.yaml")
    args = parser.parse_args()
    inventory = yaml.safe_load(args.inventory.read_text())
    desired = yaml.safe_load(args.expected.read_text())
    if inventory.get("transport") != "docker":
        parser.error("This version supports only transport: docker")
    actual_names = set(inventory["devices"])
    expected_names = set(desired["devices"])
    if actual_names != expected_names:
        parser.error(f"Inventory/expected nodes differ: {actual_names ^ expected_names}")
    if len(actual_names) != desired["fabric"]["expected_nodes"]:
        parser.error("expected_nodes does not match inventory size")

    nodes = [validate_node(name, node, desired["devices"][name])
             for name, node in inventory["devices"].items()]
    statuses = {n["status"] for n in nodes}
    fabric = "DOWN" if "DOWN" in statuses else "DEGRADED" if "DEGRADED" in statuses else "HEALTHY"
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "fabric": desired["fabric"]["name"],
              "status": fabric, "nodes": nodes}
    print("\n=== SPINE-LEAF FABRIC HEALTH CHECK ===")
    for node in nodes:
        print(f"\n{node['node'].upper()}")
        for c in node["checks"]:
            print(f"  {'PASS' if c['passed'] else 'FAIL'}  {c['name']}: {c['observed']}")
        print(f"  NODE STATUS: {node['status']}")
    print(f"\nFABRIC STATUS: {fabric}")
    folder = base / "reports"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "fabric_health_report.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Report: {path}")
    return 0 if fabric == "HEALTHY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
