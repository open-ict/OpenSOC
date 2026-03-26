
---

# 🛠️ 2. `troubleshooting.md`

👉 βάλε στο repo: `docs/troubleshooting.md`

```markdown
# OpenSOC Troubleshooting Guide

## 1. Purpose

This guide helps identify and resolve common issues during deployment and operation of OpenSOC.

---

## 2. Common Issues

### 2.1 No logs received

#### Possible causes:
- incorrect syslog configuration
- network connectivity issue
- agent not registered

#### Checks:
- verify network connectivity between VMs
- confirm syslog forwarding settings
- check Wazuh agent status

---

### 2.2 Dashboard shows no data

#### Possible causes:
- ingestion pipeline not connected
- Elasticsearch not indexing
- time range mismatch

#### Checks:
- confirm Elasticsearch is running
- check index creation
- adjust dashboard time filter

---

### 2.3 Alerts not triggering

#### Possible causes:
- rules not enabled
- thresholds too strict
- logs not matching expected format

#### Checks:
- verify rule configuration
- simulate known events
- inspect raw logs

---

### 2.4 VM performance issues

#### Possible causes:
- insufficient RAM
- disk bottlenecks
- CPU saturation

#### Checks:
- monitor resource usage in Proxmox
- increase allocated RAM
- verify storage performance

---

### 2.5 Connectivity problems

#### Possible causes:
- firewall blocking traffic
- misconfigured interfaces

#### Checks:
- verify pfSense rules
- test connectivity between VMs
- check network bridge configuration

---

## 3. Debugging Approach

1. Check infrastructure (VM status)
2. Verify connectivity
3. Inspect logs
4. Validate ingestion
5. test detection rules

---

## 4. Useful Tips

- use snapshots before major changes
- test one component at a time
- keep configurations documented
- avoid unnecessary complexity in MVP

---

## 5. Recovery

If deployment fails:

- revert to snapshot
- reapply configuration step-by-step
- validate each stage independently

---

## 6. Known Limitations

- MVP does not include advanced automation
- correlation is limited
- requires basic system administration knowledge
