# Network Automation Labs

Hands-on networking and automation labs focused on building, validating, and troubleshooting modern enterprise and datacenter networks.

This repository documents a progressive engineering journey: from manual routing labs to Python-based network validation, multi-device fabric assurance, and Ansible-driven transactional workflows.

> **Define the intended network state, compare it with reality, and make every result traceable.**

## Start Here

Choose the path that best matches what you want to explore.

### Quick Navigation

| Lab | Technology / Focus | Manual Lab | Automated / Advanced Work |
|---|---|---|---|
| **Lab 01** | OSPF | [Topology and FRR configuration](containerlab/lab01-ospf/) | [Python OSPF validation v2](containerlab/lab01-ospf/v2-automation/) |
| **Lab 02** | eBGP | [Topology and FRR configuration](containerlab/lab02-ebgp/) | [Python eBGP validation v2](containerlab/lab02-ebgp/v2-automation/) |
| **Lab 03** | iBGP Route Reflector | [Topology and FRR configuration](containerlab/lab03-ibgp-rr/) | [Python RR validation v2](containerlab/lab03-ibgp-rr/v2-automation/) |
| **Lab 04** | BGP Policy | [Topology and FRR configuration](containerlab/lab04-bgp-policy/) | [Python policy validation v2](containerlab/lab04-bgp-policy/v2-automation/) |
| **Lab 05** | Spine-Leaf eBGP + ECMP | [Manual fabric and topology](containerlab/lab05-spine-leaf-ebgp/README.md) | [Python fabric validation v2](containerlab/lab05-spine-leaf-ebgp/v2-automation/README.md) · [Ansible v3 workflows](containerlab/lab05-spine-leaf-ebgp/v3-ansible/) |

Additional foundations:
- [FRRouting OSPF with Docker Compose](frr/lab01-ospf/)
- [Netmiko and FRRouting automation exercises](automation/netmiko-frr/)

## Learning Paths

### 1. Routing and Protocol Fundamentals

Start with the manual configurations and verify each protocol directly on FRRouting.

```text
OSPF
  ↓
eBGP
  ↓
iBGP Route Reflector
  ↓
BGP Policy and Best-Path Selection
  ↓
Spine-Leaf eBGP Underlay
```

### 2. Automated Network Validation

The v2 labs turn manual checks into repeatable Python validation workflows.

```text
Define expected state
        ↓
Collect live device state
        ↓
Validate protocol and routing state
        ↓
Correlate RIB and forwarding information
        ↓
Compare actual state with intent
        ↓
Generate health results and reports
```

### 3. Transactional Network Automation

Lab 05 v3 extends validation into controlled configuration workflows using Ansible.

```text
Pre-check
   ↓
Backup
   ↓
Apply change
   ↓
Post-check
   ↓
Success? ── Yes ──> Complete
   │
   No
   ↓
Rollback
   ↓
Recovery check
```

The objective is to make changes in a controlled, verifiable, and recoverable way.

---

# Current Labs

## Lab 01 — OSPF Automated Validation

A two-router OSPF Area 0 topology using FRRouting and Containerlab.

The manual lab establishes OSPF adjacency and loopback reachability. The Python v2 validator checks:

- Expected OSPF neighbor and `Full` state.
- Remote loopback route installation.
- Source-specific loopback-to-loopback reachability.
- Overall health status and persistent reporting.

**Troubleshooting lesson:** a generic ping can use the Containerlab management network and produce a false sense of routing health. Source-specific testing is required to validate the intended path.

Explore: [Lab 01](containerlab/lab01-ospf/) · [Automated v2](containerlab/lab01-ospf/v2-automation/)

## Lab 02 — eBGP Automated Validation

A two-router, two-AS topology focused on external BGP peering and prefix exchange.

The Python v2 validator checks:

- BGP session state and expected remote AS.
- Expected prefixes and AS-path information.
- BGP route installation in the RIB.
- Source-specific reachability.
- Failure detection and recovery.

**Troubleshooting lesson:** an established BGP session does not guarantee that the expected prefixes are accepted, installed, or reachable. FRRouting import/export policy requirements must also be considered.

Explore: [Lab 02](containerlab/lab02-ebgp/) · [Automated v2](containerlab/lab02-ebgp/v2-automation/)

## Lab 03 — iBGP Route Reflector Automated Validation

A three-router iBGP topology using a Route Reflector to avoid a full-mesh design.

The Python v2 validator checks:

- iBGP session state.
- Expected reflected routes.
- Originator ID and Cluster List.
- Expected next-hop behavior.
- RIB installation and loopback reachability.
- Route Reflector client behavior.

**Troubleshooting lesson:** BGP sessions can remain established while route reflection or next-hop reachability is incorrect. In this FRRouting scenario, `next-hop-self force` was required to make the reflected paths usable by the clients.

Explore: [Lab 03](containerlab/lab03-ibgp-rr/) · [Automated v2](containerlab/lab03-ibgp-rr/v2-automation/)

## Lab 04 — BGP Policy and Intent Validation

A three-router, multi-AS topology in which R1 receives the same prefix from two upstream peers and must select the path defined by routing policy.

The Python v2 validator checks:

- Both eBGP sessions and both available paths.
- Expected Local Preference per path.
- Correct best-path selection.
- Presence of the backup path.
- Expected next-hop in the RIB.
- Routing intent rather than reachability alone.

**Troubleshooting lesson:** the network can remain reachable while selecting the wrong upstream. The validator was improved to correlate next-hop, AS path, Local Preference, and best-path state within the same BGP path, avoiding a false-positive result.

Explore: [Lab 04](containerlab/lab04-bgp-policy/) · [Automated v2](containerlab/lab04-bgp-policy/v2-automation/)

## Lab 05 — Spine-Leaf eBGP Fabric with ECMP

A four-node datacenter underlay fabric built with FRRouting, Docker, and Containerlab.

The topology contains two Spines (AS 65000) and two Leafs (AS 65101 and AS 65102). Each Leaf has eBGP connectivity to both Spines, providing redundant Layer 3 paths and two-way ECMP.

Lab 05 has evolved through three stages.

### v1 — Manual Spine-Leaf Fabric

The initial stage focuses on:

- Four-node Spine-Leaf topology.
- eBGP underlay configuration.
- Loopback advertisement and reachability.
- Redundant paths between Leafs.
- ECMP verification in FRRouting and the Linux kernel.

[Open the Lab 05 manual README](containerlab/lab05-spine-leaf-ebgp/README.md)

### v2 — Automated Fabric Health Validation

The Python validator uses YAML-based device inventory and expected state to validate the fabric.

Validation includes:

- Local BGP ASNs and expected eBGP neighbors.
- Remote AS numbers and established sessions.
- Interface operational state and IPv4 addressing.
- Loopback configuration and expected BGP prefixes.
- FRRouting RIB and Linux kernel routes.
- ECMP next-hop count.
- RIB-to-kernel next-hop consistency.
- Node and fabric health reporting.

**Troubleshooting lesson:** FRRouting can report multiple ECMP next-hops while the Linux kernel has fewer installed next-hops. Both control-plane and forwarding state must be checked.

[Open Lab 05 v2 — Automated Fabric Validation](containerlab/lab05-spine-leaf-ebgp/v2-automation/README.md)

### v3 — Ansible-Based Validation and Transactional Workflows

The v3 stage introduces Ansible-based multi-device workflows alongside the Python v2 health validator.

Completed work includes:

- Ansible validation and recovery of all eight eBGP sessions in the fabric.
- Post-workflow verification with the Python fabric health checker.
- Confirmation of two-way Leaf ECMP and FRRouting/Linux RIB consistency.
- Transactional change workflow with pre-check, configuration backup, change application, post-check, and verification.

#### v3.19 — Transactional BGP Change

A controlled BGP neighbor description change was applied to Leaf1.

The workflow completed its pre-check and backup, applied the change, passed the BGP and fabric post-checks, and then verified a manual rollback. The original configuration was restored and the drift check returned to `IN SYNC`.

#### v3.20 — Automatic Rollback

A simulated post-check failure was introduced to test the recovery path.

The Ansible workflow automatically triggered its rescue/rollback logic, removed the temporary change, restored the original configuration, and verified fabric recovery.

The transaction reported:

- Change attempted.
- Rollback verified.
- Workflow status: `ROLLED_BACK`.
- Final fabric status: `HEALTHY`.

[Explore Lab 05 v3 Ansible workflows](containerlab/lab05-spine-leaf-ebgp/v3-ansible/)

#### Next — v3.21 Automated Audit Reporting

The next planned increment will add a structured audit report using Ansible and Jinja2.

The report is intended to capture:

- Change ID.
- Device, protocol, and neighbor.
- Pre-check results.
- Backup status.
- Change application result.
- Post-check results.
- Rollback and recovery results, when applicable.
- Final fabric status and transaction outcome.

**v3.21 is planned work and is not presented as completed.**

---

## Repository Structure

The following is a high-level view of the repository. Individual lab READMEs document their detailed files and execution steps.

```text
network-automation-labs/
├── automation/
│   └── netmiko-frr/
├── containerlab/
│   ├── lab01-ospf/
│   │   ├── topology.clab.yml
│   │   └── v2-automation/
│   ├── lab02-ebgp/
│   │   ├── topology.clab.yml
│   │   └── v2-automation/
│   ├── lab03-ibgp-rr/
│   │   ├── topology.clab.yml
│   │   └── v2-automation/
│   ├── lab04-bgp-policy/
│   │   ├── topology.clab.yml
│   │   └── v2-automation/
│   └── lab05-spine-leaf-ebgp/
│       ├── topology.clab.yml
│       ├── README.md
│       ├── spine1/
│       ├── spine2/
│       ├── leaf1/
│       ├── leaf2/
│       ├── v2-automation/
│       └── v3-ansible/
├── frr/
│   └── lab01-ospf/
└── README.md
```

Generated Containerlab runtime directories, temporary outputs, and local environment files are excluded from version control where appropriate.

## Automation Philosophy

The repository progresses through three complementary engineering activities.

### 1. Understand the Network

Build the topology, configure the protocols, and verify behavior manually before automating it.

### 2. Validate the Intended State

Use Python and structured YAML data to compare expected and observed network state.

The validation approach considers multiple layers:

```text
Device reachability
       ↓
Interface state
       ↓
Protocol sessions
       ↓
Learned routes and path attributes
       ↓
FRRouting RIB
       ↓
Linux forwarding table
       ↓
End-to-end behavior
```

A device that cannot be reached must not be reported as healthy. Collection failures and network-state mismatches need to remain visible in the final report.

### 3. Apply Changes Safely

Use Ansible workflows to introduce controlled changes with pre-checks, backups, post-checks, and recovery logic.

The automation should provide evidence for an engineer to review. A failed validation or a mismatch with expected state should not automatically be treated as permission to make an unrelated corrective change.

---

## Troubleshooting-First Approach

Each lab is designed to establish a healthy baseline, introduce a controlled fault, inspect the evidence, and verify recovery.

Examples explored so far include:

- OSPF passive-interface errors.
- Incorrect BGP remote AS.
- BGP import/export policy issues.
- iBGP Route Reflector client and next-hop behavior.
- Incorrect BGP Local Preference and best-path selection.
- Spine-Leaf interface and eBGP failures.
- ECMP degradation.
- FRRouting RIB versus Linux kernel forwarding inconsistencies.
- Failed post-checks and transactional rollback.

The goal is not merely to produce a `PASS` or `FAIL`, but to identify which validation layer failed and preserve useful diagnostic evidence.

---

## Technologies

### Used in the Current Labs

- Linux networking
- Docker and Docker Compose
- Containerlab
- FRRouting (FRR) and `vtysh`
- OSPF
- eBGP and iBGP
- BGP Route Reflectors
- BGP routing policy and Local Preference
- Spine-Leaf architecture
- ECMP
- Python
- YAML
- Ansible
- Jinja2 for the planned audit-reporting workflow
- Netmiko in the standalone FRRouting automation exercises
- Git and GitHub

### Future Development

- Structured BGP JSON parsing and reusable validation modules.
- Expanded device reachability and collection-status reporting.
- VXLAN overlay validation.
- BGP EVPN control-plane validation.
- VTEP, VNI, and tenant reachability checks.
- Broader fabric-wide assurance and reporting.

---

## Roadmap

### Completed

```text
OSPF automated validation
        ↓
eBGP automated validation
        ↓
iBGP Route Reflector validation
        ↓
BGP Policy / Intent validation
        ↓
Spine-Leaf eBGP underlay + ECMP
        ↓
Python multi-device fabric validation
        ↓
Ansible transactional change workflows
        ↓
Automatic rollback and recovery verification
```

### Next

```text
v3.21 — Automated audit reporting
        ↓
VXLAN validation
        ↓
BGP EVPN validation
        ↓
Fabric-wide VXLAN/EVPN assurance
        ↓
Reusable datacenter fabric automation
```

Roadmap items are identified as planned work until their implementation and validation are complete.

---

## GitHub and Portfolio

This repository is both a hands-on learning environment and a technical portfolio. It documents not only working configurations, but also troubleshooting decisions, controlled failures, validation evidence, and recovery workflows.

The project demonstrates a progression from protocol fundamentals to network assurance and controlled multi-device automation.

- **Repository:** [NetworkJR7/network-automation-labs](https://github.com/NetworkJR7/network-automation-labs)
- **GitHub profile:** [NetworkJR7](https://github.com/NetworkJR7)

If you are arriving here from a LinkedIn post or technical discussion, start with the [Quick Navigation](#quick-navigation) table to open the manual or automated version of each lab.

## Author

**NetworkJR7** — Network Engineering, Datacenter Networking, and Network Automation.
