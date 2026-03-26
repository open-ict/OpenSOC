# OpenSOC Architecture
**Reproducible Open Security Infrastructure**

## 1. Overview

OpenSOC is a modular, self-hosted security monitoring environment built using open-source technologies and deployed through virtualization.

The architecture is designed to be:

- reproducible
- modular
- understandable
- deployable on a single host

---

## 2. Architecture Layers

### 2.1 Virtualization Layer
- Proxmox VE host
- VM-based isolation
- resource allocation per component

---

### 2.2 Network Security Layer
- Firewall (pfSense)
- routing and filtering
- log forwarding
- optional IDS/IPS extensions

---

### 2.3 Monitoring Layer
- Wazuh manager
- endpoint agents
- log ingestion
- rule-based detection

---

### 2.4 Analytics Layer
- Elasticsearch
- Kibana dashboards
- event indexing and querying

---

### 2.5 Application Layer
- alert dashboard
- event explorer
- triage interface

---

### 2.6 Lab / Validation Layer
- controlled scenarios
- test events
- detection validation
- training use

---

## 3. Data Flow

```text
Data Sources → Ingestion → Normalisation → Storage → Detection → Alerts → Dashboard
