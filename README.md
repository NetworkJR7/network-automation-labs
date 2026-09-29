# Network Automation Labs

Hands-on networking and network automation labs focused on building practical skills from foundational networking concepts to scalable enterprise and datacenter automation.

## Mission

This repository documents a progressive journey in modern network engineering.

The goal is to start with networking fundamentals, Linux, containers, routing protocols and small automation tasks, then progressively move toward larger and more complex enterprise and datacenter environments.

Rather than treating automation as a separate subject, the labs combine **networking, troubleshooting and automation** from the beginning.

The long-term objective is to develop the skills required to **deploy, validate, troubleshoot and automate network infrastructures reliably and at scale**.

---

## Learning Path

```text
Linux Networking
       ↓
Docker
       ↓
FRRouting
       ↓
OSPF
       ↓
Containerlab
       ↓
eBGP
       ↓
iBGP / Route Reflector
       ↓
BGP Policy
       ↓
Python
       ↓
Netmiko
       ↓
Ansible
       ↓
Spine-Leaf Architecture
       ↓
VXLAN
       ↓
BGP EVPN
       ↓
Automated Validation
       ↓
Fault Detection & Troubleshooting
       ↓
Scalable Datacenter Automation
```

---

## Repository Structure

```text
network-labs/
│
├── frr/
│   └── lab01-ospf/
│
├── containerlab/
│   ├── lab01-ospf/
│   ├── lab02-ebgp/
│   ├── lab03-ibgp-rr/
│   └── lab04-bgp-policy/
│
├── automation/
│   └── netmiko-frr/
│
├── ansible/
├── docker/
├── python/
│
└── README.md
```

---

# Current Labs

## FRRouting

### Lab 01 — OSPF with Docker Compose

Introduction to FRRouting using containers.

Main topics:

- FRRouting configuration
- Docker Compose
- IPv4 addressing
- OSPF
- Neighbor establishment
- Routing table verification
- Loopback reachability
- Basic troubleshooting

Typical verification commands:

```bash
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip route"
vtysh -c "show running-config"
```

---

## Containerlab

Containerlab is used to build reproducible multi-router network topologies with FRRouting.

### Lab 01 — OSPF

Two-router OSPF topology using FRRouting and Containerlab.

Topics:

- Containerlab topology definition
- FRR configuration
- OSPF Area 0
- Neighbor establishment
- Route exchange
- Connectivity validation

---

### Lab 02 — eBGP

Introduction to External BGP.

Topics:

- Different Autonomous Systems
- eBGP neighbor establishment
- Network advertisement
- BGP routing table
- Best-path verification
- End-to-end reachability

Example verification:

```bash
show bgp summary
show bgp ipv4 unicast
show ip route bgp
```

---

### Lab 03 — iBGP Route Reflector

Multi-router iBGP topology implementing a Route Reflector.

Topics:

- iBGP
- Route Reflector
- RR clients
- Originator ID
- Cluster ID
- Next-hop behavior
- `next-hop-self`
- BGP route propagation

This lab explores how Route Reflectors reduce the need for a full-mesh iBGP topology.

---

### Lab 04 — BGP Policy

Introduction to BGP path manipulation and routing policy.

Topics include:

- BGP path selection
- Local Preference
- Route Maps
- Prefix filtering
- Policy application
- Routing verification
- Troubleshooting incorrect path selection

The goal is to move beyond basic BGP connectivity and understand how routing decisions can be controlled.

---

# Network Automation

## Netmiko + FRRouting

The first automation lab introduces Python-based device interaction using Netmiko.

The objective is to move from manual CLI operations such as:

```bash
show ip route
show bgp summary
show running-config
```

toward automated command execution and result collection.

Current capabilities include:

- SSH connectivity
- Automated command execution
- FRRouting interaction
- Output collection
- Saving command results to files
- Basic validation workflow

Example concept:

```text
Python Script
     │
     ▼
  Netmiko
     │
     ▼
FRRouting Node
     │
     ▼
Show Commands
     │
     ▼
Collected Output
```

This is the foundation for more advanced network validation and troubleshooting automation.

---

# Automation Philosophy

The objective of these labs is not simply to automate configuration.

A reliable network automation workflow should include:

```text
Inventory
    ↓
Connection
    ↓
Data Collection
    ↓
Validation
    ↓
Decision
    ↓
Configuration
    ↓
Verification
    ↓
Reporting
```

Automation should be able to answer questions such as:

```text
Are all OSPF neighbors established?

Are all BGP sessions up?

Are the expected routes present?

Is the correct BGP path selected?

Are all VTEPs reachable?

Are VXLAN VNIs operational?

Are EVPN routes being exchanged?

Is the fabric healthy?
```

Eventually the objective is to produce automated health checks such as:

```text
OSPF              PASS
BGP               PASS
BGP EVPN          PASS
VTEP Reachability PASS
VXLAN             PASS
Route Validation  PASS

FABRIC STATUS: HEALTHY
```

---

# Roadmap

The repository will progressively expand into more advanced networking and automation topics.

## Python for Networking

- Variables and data structures
- Lists and dictionaries
- Loops
- Functions
- JSON
- YAML
- Exception handling
- File operations
- Network inventory management

---

## Netmiko

- Multi-device connections
- Command execution
- Configuration deployment
- Output parsing
- Health checks
- Error handling
- Logging
- Automated troubleshooting

---

## Ansible

- Inventory management
- Variables
- Playbooks
- Templates
- Jinja2
- Automated configuration deployment
- Configuration validation
- Idempotent network changes

---

## Datacenter Networking

Future labs will introduce modern datacenter technologies including:

- Spine-Leaf architecture
- Underlay and overlay networks
- eBGP underlay
- VXLAN
- VTEPs
- VNIs
- BGP EVPN
- EVPN Route Types
- Distributed Layer 2 and Layer 3 services

---

## Datacenter Automation

The final stages of the learning path will combine networking and automation.

Example target architecture:

```text
            Automation
          Python / Ansible
                │
                ▼
       ┌─────────────────┐
       │     SPINE       │
       └───────┬─────────┘
          eBGP │ Underlay
     ┌─────────┼─────────┐
     │         │         │
     ▼         ▼         ▼
   LEAF1     LEAF2     LEAF3
     │         │         │
     └──── VXLAN / EVPN ─┘
```

Automation will eventually handle:

- Device inventory
- Configuration generation
- BGP deployment
- VXLAN configuration
- EVPN configuration
- Pre-change validation
- Post-change validation
- Health checks
- Fault detection
- Automated troubleshooting
- Network state reporting

---

# Technologies

Technologies used or planned in this repository include:

- Linux Networking
- Docker
- Docker Compose
- FRRouting
- Containerlab
- OSPF
- BGP
- eBGP
- iBGP
- Route Reflectors
- BGP Policy
- Python
- Netmiko
- Ansible
- Jinja2
- VXLAN
- BGP EVPN
- Git
- GitHub

---

# Troubleshooting First

Troubleshooting is an important part of every lab.

Each topology is intended not only to demonstrate a working configuration but also to help understand why networks fail.

Typical troubleshooting areas include:

- Incorrect IP addressing
- OSPF adjacency failures
- MTU mismatches
- Missing routing advertisements
- BGP neighbor failures
- Incorrect ASN configuration
- Next-hop reachability problems
- Route Reflector configuration errors
- Routing policy mistakes
- VXLAN VTEP connectivity
- EVPN control-plane issues

The objective is to understand both:

```text
How to build it
```

and:

```text
How to troubleshoot it when it breaks
```

---

# Long-Term Goal

The final goal of this repository is to progress from small networking labs toward automated enterprise and datacenter fabrics.

```text
Manual Networking
        ↓
CLI Verification
        ↓
Python Automation
        ↓
Multi-Device Automation
        ↓
Configuration Generation
        ↓
Automated Validation
        ↓
Automated Troubleshooting
        ↓
Datacenter Fabric Automation
        ↓
Network Automation at Scale
```

This repository is therefore not intended to be a collection of isolated exercises.

It is a **progressive engineering lab environment** for learning how modern networks are built, operated, validated and automated.

---

## Related Projects

More advanced and specialized projects are maintained separately, including labs focused on:

- BGP Route Reflectors
- Spine-Leaf networking
- VXLAN
- EVPN
- EVPN fabric automation
- Automated network health checks

These projects expand on the foundations developed in this repository.
