# OpenSOC Deployment Guide
**Reproducible Open Security Infrastructure for Small Organisations**

## 1. Purpose

This guide describes how to deploy the OpenSOC MVP in a small, self-hosted virtualized environment.

The goal is to provide a reproducible setup that combines:

- network security
- endpoint monitoring
- centralized logging
- alerting
- dashboard-based visibility

The MVP is designed to run on a single virtualization host.

---

## 2. Reference Architecture

OpenSOC MVP uses the following virtual machines:

- **VM1: pfSense**
  - firewall
  - network boundary
  - syslog forwarding

- **VM2: Wazuh**
  - event collection
  - monitoring
  - detection rules

- **VM3: ELK**
  - indexing
  - search
  - dashboards

Optional:

- **VM4: Ubuntu test endpoint**
- **VM5: Windows test endpoint**

---

## 3. Host Requirements

### Minimum
- 8-core CPU
- 32 GB RAM
- 500 GB SSD/NVMe
- 2 network interfaces preferred
- Proxmox VE installed

### Recommended
- 12+ cores
- 64 GB RAM
- 1 TB NVMe
- separate network/storage planning
- UPS for stability

---

## 4. Virtualization Layer

OpenSOC uses **Proxmox VE** as the virtualization layer.

### Suggested VM allocation

| VM | Role | vCPU | RAM | Disk |
|----|------|------|-----|------|
| pfSense | Firewall | 2 | 4 GB | 32 GB |
| Wazuh | Monitoring | 4 | 8 GB | 120 GB |
| ELK | Analytics | 4 | 8 GB | 120 GB |
| Ubuntu Test | Test endpoint | 2 | 4 GB | 40 GB |
| Windows Test | Test endpoint | 2 | 4–8 GB | 64 GB |

These values are indicative and can be adjusted.

---

## 5. Network Design

A simple MVP topology can include:

- **WAN / external side**
- **LAN / internal monitored network**
- optional **management network**

### Basic logic
- pfSense acts as the gateway
- monitored systems are placed behind pfSense
- logs are forwarded to OpenSOC components
- dashboard access is restricted to admin/operator users

---

## 6. Deployment Steps

## Step 1 — Prepare Proxmox host
- install Proxmox VE
- configure storage
- configure bridge networking
- update host
- document host IP and admin access

## Step 2 — Create core VMs
Create the following VMs:
- pfSense
- Wazuh
- ELK

Optional:
- Ubuntu test VM
- Windows test VM

## Step 3 — Configure pfSense
- assign interfaces
- configure LAN/WAN
- enable syslog forwarding
- define basic firewall policy
- enable optional IDS/IPS extensions later if needed

## Step 4 — Configure Wazuh
- install Wazuh manager
- configure agents / agent registration
- verify event collection
- enable initial ruleset

## Step 5 — Configure ELK
- deploy Elasticsearch
- deploy Kibana
- connect ingestion pipeline
- create baseline dashboards

## Step 6 — Connect data flow
- forward firewall logs
- register Linux endpoint
- register Windows endpoint
- validate event arrival and indexing

## Step 7 — Enable alert workflow
- activate baseline detections
- configure severity levels
- validate alert display in dashboard

## Step 8 — Run validation scenario
- generate repeated failed login attempts
- confirm alert generation
- inspect event timeline
- document findings

---

## 7. Data Flow

The MVP data flow is:

```text
Firewall / Endpoints → Ingestion → Normalisation → Storage → Detection → Alerts → Dashboard
