# Lab 05 v2 — Automated Spine-Leaf eBGP Fabric Validation

## Overview

This project extends Lab 05 v1 by introducing automated
network validation using Python.

Instead of manually checking each router, the validator
collects operational data and compares it against a
declarative expected-state model.

## Architecture

```text
inventory.yaml ────────────────┐
                               v
                      Python Health Checker <──── expected_state.yaml
                               |
                         Docker Transport
                               |
                         FRRouting / Linux
                               |
                        Validation Engine
                               |
                           NODE STATUS
                               |
                           FABRIC STATUS
```

## Components

| File | Purpose |
|---|---|
| inventory.yaml | Device inventory and transport information |
| expected_state.yaml | Expected routing and interface state |
| fabric_health_check.py | Multi-node validation engine |
| reports/ | JSON validation evidence |

## Validation Scope

The Python validator checks:

- Local BGP autonomous system numbers.
- Expected eBGP neighbors.
- Remote AS numbers.
- Established BGP sessions.
- Interface operational state.
- Interface IP addressing.
- Loopback configuration.
- Expected BGP prefixes.
- FRRouting routing table.
- Linux kernel routes.
- ECMP nexthop counts.
- RIB-to-kernel nexthop consistency.

## Requirements
- Python 3
- PyYAML
- Docker
- Containerlab
- FRRouting containers

Install PyYAML in a Python virtual environment if needed.

## Execution
From the Lab 05 root directory:
```bash
python3 v2-automation/fabric_health_check.py
```

## Expected Healthy State

```text
SPINE1  — NODE STATUS: HEALTHY
SPINE2  — NODE STATUS: HEALTHY
LEAF1   — NODE STATUS: HEALTHY
LEAF2   — NODE STATUS: HEALTHY

FABRIC STATUS: HEALTHY
```

## Health Classification
The validator produces three operational states.
### HEALTHY
All required checks pass.
### DEGRADED
One or more checks fail, but the condition has not been
classified as a complete loss of service.

Examples include missing BGP redundancy or incomplete ECMP.
### DOWN
A critical collection failure or a condition classified
as critical prevents successful validation.

Health classification reflects the implemented validation
logic and should not be interpreted as a complete production
service-impact assessment.

## Fault Injection

### Scenario 01 — ECMP Degradation
An interface shutdown was used to simulate a failure
between Leaf1 and Spine1.
```bash
docker exec clab-frr-spine-leaf-leaf1 \
  ip link set eth1 down
```

The validator detected a reduction in the number of
kernel nexthops.

Observed result:

```text
NODE STATUS: DEGRADED
FABRIC STATUS: DEGRADED
```

### Scenario 02 — BGP Connectivity Loss
During recovery troubleshooting, Leaf1 was observed without
its data interfaces.

Both BGP sessions transitioned to Active, and expected
routes disappeared.

This incident was captured by the earlier validator,
which reported a DEGRADED fabric state.

The validator was subsequently enhanced with interface
health checks and improved status classification.

## RIB and Kernel Consistency

One important finding was a mismatch between the nexthops
reported by FRRouting and those present in the Linux kernel.

FRRouting reported:

```text
10.0.11.0 via eth1
10.0.21.0 via eth2
```

The Linux kernel nexthop group contained only:

```text
10.0.21.0 via eth2
```

The validation process identified this missing kernel nexthop. The v2.1 checker now includes an explicit RIB-to-kernel consistency check.

This demonstrates why checking only BGP Established state
or FRRouting's routing table is insufficient for validating
ECMP forwarding state.

## Recovery

After preserving diagnostic evidence, the Containerlab
topology was destroyed and redeployed.

The reconstructed fabric restored:
- Four eBGP adjacencies (two per leaf, four unique links).
- Expected BGP routes.
- Two ECMP nexthops on both Leafs.
- Matching FRRouting and Linux nexthop information.
Final validation:

```text
FABRIC STATUS: HEALTHY
```

## Reports
The repository includes representative JSON reports:
| Report | Description |
|---|---|
| `fabric_baseline_healthy.json` | Initial healthy baseline |
| `fabric_fault01_degraded.json` | ECMP degradation |
| `fabric_fault02_bgp_down.json` | BGP connectivity incident (historical `DEGRADED` classification) |
| `fabric_v2_1_healthy.json` | Final enhanced validation |


The automatically regenerated fabric_health_report.json is
excluded from Git.

## Engineering Lessons
This lab demonstrates that:
1. Established BGP sessions do not guarantee route reachability.
2. Multiple BGP paths do not automatically guarantee ECMP.
3. FRRouting and Linux routing state should be validated independently.
4. Network automation should compare actual state against declared expectations.
5. Fault injection helps validate monitoring and troubleshooting logic.

## Future Improvements
- Structured BGP JSON parsing.
- Additional reachability testing.
- Unit tests for route parsers.
- Multi-vendor transport support.
- CI-based validation.
- Automated fault-injection workflows.

## Author

NetworkJR7 — Network Automation & Datacenter Networking
