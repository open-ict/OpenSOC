
---

## LAB-GUIDE.md

```markdown
# OpenSOC Lab Guide
**Hands-on validation environment for reproducible security monitoring**

## Goal

This lab demonstrates how OpenSOC can be deployed and validated in a small virtualized environment.

The purpose of the lab is to show:

- event ingestion
- detection logic
- alert generation
- analyst visibility
- reproducible training scenarios

---

## Lab Topology

### Virtual Machines

- **VM1: pfSense**
  - gateway / firewall
  - syslog export

- **VM2: Wazuh**
  - monitoring server
  - detection rules
  - agent management

- **VM3: ELK**
  - indexing
  - analytics
  - dashboards

- **VM4: Ubuntu test machine**
  - SSH service
  - Linux logs
  - attack simulation target

- **VM5: Windows test endpoint**
  - event logs
  - process execution simulation

---

## Minimum Resources

Suggested single-host environment:

- 32 GB RAM minimum
- multi-core CPU
- SSD/NVMe storage
- Proxmox VE installed

---

## Lab Objectives

1. Deploy a reproducible OpenSOC stack
2. Connect firewall and endpoint logs
3. Validate event flow end-to-end
4. Trigger alerts through controlled test activity
5. Review alerts in dashboard and triage workflow

---

## Scenario A: Repeated Failed SSH Access

### Steps
1. Enable SSH on Ubuntu test VM
2. Attempt multiple failed logins from another test machine
3. Confirm logs are ingested
4. Verify brute-force or repeated failure alert appears

### Expected outcome
- multiple authentication failure events visible
- alert triggered in dashboard
- event timeline available for review

---

## Scenario B: Successful Login After Failures

### Steps
1. After repeated failed attempts, perform a successful login
2. Execute a few test commands
3. Generate suspicious-looking activity markers

### Expected outcome
- correlation between failed and successful login
- incident becomes more visible in triage workflow
- analyst can inspect timeline

---

## Scenario C: Endpoint Test Event

### Steps
1. Execute a known test command or benign simulated suspicious action on Windows endpoint
2. Confirm event ingestion
3. Validate display in dashboard

### Expected outcome
- endpoint event visible
- mapped to host
- available for correlation and triage

---

## Validation Checklist

- [ ] All VMs boot successfully
- [ ] Firewall logs forwarded
- [ ] Endpoint logs ingested
- [ ] Dashboard accessible
- [ ] Alerts visible
- [ ] Demo scenario reproducible
- [ ] Documentation sufficient for re-deployment

---

## Educational Use

This lab can also be used for:

- cybersecurity workshops
- SME awareness training
- basic SOC workflow education
- open infrastructure demonstrations

---

## Notes

The lab uses controlled simulation and does not require advanced offensive tooling.  
Its purpose is to validate monitoring workflows and improve accessibility of open cybersecurity infrastructure.
