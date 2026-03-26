# OpenSOC
**Reproducible Open Security Infrastructure for Small Organisations**

OpenSOC is an open-source, self-hosted “SOC-in-a-box” designed for small organisations, educational environments, and community labs.

It provides a reproducible security monitoring environment built on open technologies and deployable on a single virtualization host.

---

## Overview

OpenSOC does not create new security tools from scratch.  
Instead, it integrates proven open-source components into a reusable, documented, and understandable deployment model.

The project focuses on:

- reproducibility
- self-hosting
- modular architecture
- practical security visibility
- educational and operational use

---

## Core Components

OpenSOC is built around a virtualized architecture using:

- **Proxmox VE** as the virtualization layer
- **pfSense** as firewall and network boundary
- **Wazuh** for monitoring and detection
- **ELK Stack** for analytics and visualization

---

## Architecture

### Main layers

1. **Virtualization Layer**
   - Proxmox host
   - VM-based deployment
   - isolated security services

2. **Security Layer**
   - firewall
   - network monitoring
   - optional IDS/IPS extensions

3. **Monitoring Layer**
   - log collection
   - endpoint monitoring
   - rule-based alerts

4. **Analytics Layer**
   - indexing
   - event processing
   - dashboards

5. **Lab / Validation Layer**
   - test scenarios
   - demo detections
   - validation workflows

---

## MVP Scope

The initial MVP includes:

- single Proxmox host deployment
- pfSense VM
- Wazuh VM
- ELK / dashboard VM
- basic ingestion and normalization
- rule-based alerting
- one reproducible demo attack scenario
- deployment documentation

---

## Use Cases

OpenSOC is intended for:

- small organisations
- SMEs without enterprise SOC budgets
- training labs
- educational environments
- community infrastructure
- cooperative and civic organisations

---

## Repository Structure

```text
opensoc/
├── deploy/
├── docs/
├── scenarios/
├── configs/
├── dashboard/
└── README.md
