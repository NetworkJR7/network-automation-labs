# Network Automation Labs

Hands-on networking and automation labs built to explore how modern networks are designed, validated, and troubleshot.

The repository progresses from protocol fundamentals and manual CLI verification to Python-based expected-state validation. Each automated lab checks more than reachability: it correlates control-plane state, routing information, forwarding behavior, and the intended network outcome.

> **Start here:** Choose a protocol in [Quick Navigation](#quick-navigation). Open the **Manual Lab** to study the topology and FRRouting configuration, or go directly to **Automated v2** to review the validation workflow, fault injection, and health report.

## Start Here

There are two ways to use this repository:

1. **Learn and troubleshoot the network manually** — inspect the topology, review the FRRouting configuration, deploy the lab, and verify protocol behavior from the CLI.
2. **Study network validation automation** — inspect the expected state, run the Python health check, introduce a controlled fault, and confirm that the failure is detected and reported.

New to the project? Follow the labs in order:

```text
OSPF → eBGP → iBGP Route Reflector → BGP Policy
```

Interested mainly in automation? Start with [Lab 01 v2](containerlab/lab01-ospf/v2-automation/README.md) and follow the progression from adjacency checks to routing-intent validation.

## Quick Navigation

| Lab | Focus | Manual Lab | Automated v2 |
|---|---|---|---|
| Lab 01 | OSPF | [Topology and FRR configuration](containerlab/lab01-ospf/) | [OSPF automated validation](containerlab/lab01-ospf/v2-automation/README.md) |
| Lab 02 | eBGP | [Topology and FRR configuration](containerlab/lab02-ebgp/) | [eBGP automated validation](containerlab/lab02-ebgp/v2-automation/README.md) |
| Lab 03 | iBGP Route Reflector | [Topology and FRR configuration](containerlab/lab03-ibgp-rr/) | [Route Reflector automated validation](containerlab/lab03-ibgp-rr/v2-automation/README.md) |
| Lab 04 | BGP Policy | [Topology and FRR configuration](containerlab/lab04-bgp-policy/) | [BGP policy and intent validation](containerlab/lab04-bgp-policy/v2-automation/README.md) |
| Lab 05 | Spine-Leaf eBGP + ECMP | [Spine-Leaf topology and FRR configuration](containerlab/lab05-spine-leaf-ebgp/README.md) | [Automated fabric validation](containerlab/lab05-spine-leaf-ebgp/v2-automation/README.md) |

Additional foundations:

- [FRRouting OSPF lab with Docker Compose](frr/lab01-ospf/)
- [Netmiko and FRRouting automation exercise](automation/netmiko-frr/)

## Learning Paths

### 1. Routing Fundamentals

Use the manual labs to understand protocol behavior before automating it.

```text
OSPF adjacency and route exchange
              ↓
eBGP peering and path learning
              ↓
iBGP scaling with a Route Reflector
              ↓
BGP path selection and routing policy
```

### 2. Network Automation and Validation

Use the v2 labs to turn operational checks into repeatable validation.

```text
Define expected state
          ↓
Collect live network state
          ↓
Validate control plane, RIB, and data plane
          ↓
Return clear PASS / FAIL results
          ↓
Generate a persistent health report
```

### 3. Troubleshooting Practice

Treat each healthy topology as a baseline, introduce one controlled failure, and work through the evidence in layers:

```text
Session or adjacency → Learned paths → Installed route → Forwarding → Intended outcome
```

## Manual Labs vs Automated v2

The two versions serve different but complementary purposes.

| Manual Lab | Automated v2 |
|---|---|
| Defines the Containerlab topology | Reuses the same network topology |
| Contains the FRRouting configuration | Adds an expected-state inventory |
| Encourages direct CLI inspection | Collects operational state programmatically |
| Builds protocol and troubleshooting knowledge | Produces repeatable PASS / FAIL checks |
| Answers “how does this protocol behave?” | Answers “is the network behaving as designed?” |

The v2 labs are not configuration-deployment pipelines. Their current focus is **automated validation and fault detection**. The Python scripts interact with the running FRRouting containers, parse relevant state, compare it with the expected outcome, and write a health report.

## Current Labs

### Lab 01 — OSPF

A two-router Area 0 topology focused on adjacency formation, route learning, and loopback reachability.

The automated version validates:

- Expected OSPF neighbors in `Full` state
- OSPF-learned loopback routes
- Source-specific loopback-to-loopback reachability
- Persistent healthy or unhealthy status reporting

It also demonstrates why a generic ping can be misleading when a separate management network exists.

**Explore:** [Manual Lab](containerlab/lab01-ospf/) · [Automated v2](containerlab/lab01-ospf/v2-automation/README.md)

### Lab 02 — eBGP

A two-AS topology introducing external BGP peering, prefix exchange, AS-path inspection, RIB installation, and end-to-end reachability.

The automated version validates:

- BGP session state and expected remote ASN
- Expected prefixes and AS-path information
- BGP routes installed in the routing table
- Source-specific data-plane reachability
- Failure detection and recovery evidence

The central lesson is that an established BGP session is necessary, but it is not sufficient proof of a healthy service.

**Explore:** [Manual Lab](containerlab/lab02-ebgp/) · [Automated v2](containerlab/lab02-ebgp/v2-automation/README.md)

### Lab 03 — iBGP Route Reflector

A three-router iBGP topology using a Route Reflector to avoid a full-mesh design.

The automated version validates:

- iBGP session state
- Correct route reflection between clients
- Originator ID and Cluster ID
- Expected next-hop behavior
- RIB installation and loopback reachability
- Route Reflector client and non-client failure scenarios

This lab moves validation beyond simple prefix presence and checks the attributes that explain how and why a route was propagated.

**Explore:** [Manual Lab](containerlab/lab03-ibgp-rr/) · [Automated v2](containerlab/lab03-ibgp-rr/v2-automation/README.md)

### Lab 04 — BGP Policy

A three-router, multi-AS topology in which R1 receives the same prefix from two upstream peers and must prefer the path defined by routing policy.

The automated version validates:

- Both eBGP sessions and both available paths
- Local Preference on the preferred path
- Correct best-path selection
- Presence of a non-best backup path
- Expected next-hop in the RIB
- End-to-end routing intent, not only protocol state

This is the first lab in the series to frame network health explicitly as **intent validation**: reachability may still exist while the selected path is wrong.

**Explore:** [Manual Lab](containerlab/lab04-bgp-policy/) · [Automated v2](containerlab/lab04-bgp-policy/v2-automation/README.md)

### Lab 05 — Spine-Leaf eBGP Fabric with ECMP

A four-node datacenter underlay fabric built with FRRouting, Docker, and Containerlab.

The topology consists of two Spines (AS 65000) and two Leafs (AS 65101 and AS 65102), providing redundant Layer 3 connectivity through eBGP and two-way ECMP.

The automated version validates:

- eBGP neighbor establishment and remote ASNs
- Interface operational state and IPv4 addressing
- Loopback advertisements and expected BGP prefixes
- FRRouting RIB and Linux kernel routing tables
- ECMP nexthop count and RIB-to-kernel consistency
- Fabric-wide health status and JSON reporting

**Troubleshooting highlight:** Fault injection revealed an ECMP inconsistency between FRRouting and the Linux kernel. The Python validator was enhanced to detect this condition automatically.

**Explore:** [Manual Lab](containerlab/lab05-spine-leaf-ebgp/README.md) · [Automated v2](containerlab/lab05-spine-leaf-ebgp/v2-automation/README.md)

## Repository Structure

```text
network-automation-labs/
├── automation/
│   └── netmiko-frr/
│       ├── netmiko_test.py
│       ├── topology.clab.yml
│       ├── r1/
│       └── outputs/
│
├── containerlab/
│   ├── lab01-ospf/
│   │   ├── topology.clab.yml
│   │   ├── r1/
│   │   ├── r2/
│   │   └── v2-automation/
│   │       ├── README.md
│   │       ├── inventory.yaml
│   │       ├── ospf_health_check.py
│   │       ├── images/
│   │       └── reports/
│   │
│   ├── lab02-ebgp/
│   │   ├── topology.clab.yml
│   │   ├── r1/
│   │   ├── r2/
│   │   └── v2-automation/
│   │       ├── README.md
│   │       ├── inventory.yaml
│   │       ├── bgp_health_check.py
│   │       ├── images/
│   │       └── reports/
│   │
│   ├── lab03-ibgp-rr/
│   │   ├── topology.clab.yml
│   │   ├── r1/
│   │   ├── r2/
│   │   ├── r3/
│   │   └── v2-automation/
│   │       ├── README.md
│   │       ├── inventory.yaml
│   │       ├── rr_health_check.py
│   │       ├── images/
│   │       └── reports/
│   │
│   ├── lab04-bgp-policy/
│   │   ├── topology.clab.yml
│   │   ├── r1/
│   │   ├── r2/
│   │   ├── r3/
│   │   └── v2-automation/
│   │       ├── README.md
│   │       ├── inventory.yaml
│   │       ├── policy_health_check.py
│   │       ├── images/
│   │       └── reports/
│   │
│   └── lab05-spine-leaf-ebgp/
│       ├── README.md
│       ├── topology.clab.yml
│       ├── images/
│       │   └── lab05-spine-leaf-ebgp.png
│       ├── spine1/
│       ├── spine2/
│       ├── leaf1/
│       ├── leaf2/
│       └── v2-automation/
│           ├── README.md
│           ├── inventory.yaml
│           ├── expected_state.yaml
│           ├── fabric_health_check.py
│           └── reports/
├── frr/
│   └── lab01-ospf/
│       ├── docker-compose.yml
│       ├── r1/
│       └── r2/
│
└── README.md
```

## Automation Philosophy

Automation is most useful when it verifies an intended outcome, not when it merely repeats CLI commands faster.

The working model in this repository is:

```text
Topology and routing intent
            ↓
Expected state in YAML
            ↓
Operational data collection
            ↓
Protocol-aware validation
            ↓
Control plane + RIB + data plane correlation
            ↓
PASS / FAIL result and health report
```

The core principles are:

- **Expected state before validation** — define what healthy means for each node and protocol.
- **Multiple layers of evidence** — a session being up does not prove that routes, forwarding, or policy are correct.
- **Clear failure signals** — checks should identify the layer that failed, not only return a generic error.
- **Persistent reporting** — every automated lab writes a report that can be reviewed after execution.
- **Troubleshooting value** — automation should reduce the time between detecting a symptom and locating the likely fault domain.

## Troubleshooting First

Every lab is designed to answer two questions:

```text
How does the network work when it is healthy?
How does the failure appear at each validation layer?
```

The v2 documentation includes controlled fault scenarios and recovery steps. Typical investigation areas include:

- Incorrect addressing or autonomous system numbers
- OSPF adjacency failures
- BGP session failures
- Missing or incorrect route advertisements
- Unreachable BGP next hops
- Incorrect Route Reflector client relationships
- Routes present in BGP but absent from the RIB
- Routing-policy errors and incorrect best-path selection
- False-positive reachability through the management network

Useful FRRouting commands across the labs include:

```text
show ip ospf neighbor
show ip route
show bgp summary
show bgp ipv4 unicast
show ip route bgp
show running-config
```

## Technologies

### Used in the Current Repository

- Linux networking
- Docker and Docker Compose
- Containerlab
- FRRouting (FRR) and `vtysh`
- OSPF, eBGP, iBGP, Route Reflectors, and BGP policy
- Python
- YAML-based expected-state inventories
- `subprocess` and `docker exec` for v2 state collection
- Netmiko in the standalone FRRouting automation exercise
- Git and GitHub

### Planned for Future Stages

- Configuration generation and reusable templates
- Ansible and Jinja2 workflows
- Pre-change and post-change validation
- VXLAN data plane and VTEP validation
- BGP EVPN control plane
- Reusable multi-device validation across different topologies
- Extended fabric-wide health checks for VXLAN/EVPN
## Roadmap

Labs 01–05 and their automated v2 validation workflows are the current completed progression in this repository. The next stages are intentionally listed as roadmap items, not as completed implementations.

### Next — Scale the Validation Model

- Replace lab-specific assumptions with a multi-device inventory model
- Express expected neighbors, prefixes, attributes, and next hops as reusable data
- Produce aggregated results across the topology
- Improve parsing, exception handling, and failure summaries
- Add repeatable pre-change and post-change checks

### Completed — Spine–Leaf eBGP Underlay

- Four-node Spine-Leaf architecture using FRRouting and Containerlab
- eBGP underlay with two-way ECMP
- Automated interface, BGP, RIB, and kernel validation
- Fault-injection and recovery evidence

### Next — VXLAN and BGP EVPN

- Introduce VTEPs, VNIs, and overlay reachability
- Add the BGP EVPN address family and relevant EVPN route types
- Correlate EVPN control-plane state with VXLAN data-plane state
- Validate VTEP reachability, VNI presence, and tenant connectivity

### Target — Fabric Automation

- Generate device configuration from structured data
- Apply consistent changes across multiple nodes
- Validate intended state before and after a change
- Detect protocol, policy, and forwarding failures at fabric scale
- Produce a consolidated fabric health report

```text
Completed: OSPF → eBGP → iBGP RR → BGP Policy → Spine-Leaf eBGP + ECMP
Next:      VXLAN → BGP EVPN → Fabric Automation
```

## GitHub and Portfolio

This repository is both a learning environment and a technical portfolio. It is intended to make the engineering process visible, not only the final working configuration.

The project demonstrates:

- Progressive routing-protocol labs built with reproducible container topologies
- FRRouting configuration and protocol verification
- Troubleshooting through controlled fault injection
- Python automation based on expected versus actual state
- Validation across the control plane, routing table, and data plane
- Clear technical documentation, diagrams, and saved health reports

**Repository:** [NetworkJR7/network-automation-labs](https://github.com/NetworkJR7/network-automation-labs)  
**GitHub profile:** [github.com/NetworkJR7](https://github.com/NetworkJR7)

If you arrived here from a portfolio post or technical discussion, [Quick Navigation](#quick-navigation) is the fastest way to compare the manual protocol work with its automated validation layer.

## Project Direction

The long-term goal is to move from small, protocol-focused exercises toward repeatable validation and automation for enterprise and datacenter networks.

```text
Manual networking
        ↓
Protocol-aware troubleshooting
        ↓
Expected-state validation
        ↓
Multi-device automation
        ↓
Datacenter fabric validation
        ↓
Reliable network automation at scale
```

This is an evolving hands-on project. Completed work is documented as current labs; planned technologies remain clearly identified in the roadmap.
