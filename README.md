# 🛡️ OpenSOC
**Open Security Monitoring Stack for Small Organisations**

OpenSOC is an open-source, self-hosted security monitoring platform that enables small organisations to deploy a practical and reproducible security infrastructure using open technologies.

---

## 🚀 Overview

OpenSOC provides a complete, deployable security monitoring environment by integrating existing open-source tools into a unified system.

It focuses on:
- Simplicity
- Reproducibility
- Self-hosting
- Modular architecture

---

## 🧩 Architecture

OpenSOC is built on a virtualized infrastructure using:

- Proxmox VE (virtualization layer)
- pfSense (network security)
- Wazuh (monitoring & detection)
- ELK Stack (analytics & visualization)

---

## 🖥️ System Layers

### 1. Virtualization Layer
- Proxmox-based infrastructure
- Virtual Machines for isolation
- Container support

### 2. Security Layer
- Firewall (pfSense)
- IDS/IPS (Suricata optional)
- Network monitoring

### 3. Monitoring Layer
- Log collection (Wazuh agents)
- Endpoint visibility
- Rule-based detection

### 4. Analytics Layer
- Event processing
- Data indexing (Elasticsearch)
- Visualization (Kibana)

### 5. Application Layer
- Alert dashboard
- Event exploration
- Triage workflow

---

## 🔄 Data Flow
