## Τίτλος
**OpenSOC – Reproducible Virtualized Security Infrastructure**

## Subtitle
**SOC-in-a-box for small organisations, education, and community labs**

---

## Diagram layout

```text
┌──────────────────────────────────────────────────────────────┐
│                           OpenSOC                            │
│      Reproducible Open Security Infrastructure Platform      │
└──────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│                    Virtualization Layer                      │
│                       Proxmox VE Host                        │
└──────────────────────────────────────────────────────────────┘
                │
                │ hosts isolated security services
                ▼

┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│   Firewall VM      │  │   Monitoring VM    │  │    Analytics VM    │
│--------------------│  │--------------------│  │--------------------│
│ pfSense            │  │ Wazuh Manager      │  │ Elasticsearch       │
│ Routing / Filtering│  │ Agent Events       │  │ Kibana Dashboards   │
│ Syslog Export      │  │ Rule Evaluation    │  │ Search / Visualize  │
└─────────┬──────────┘  └─────────┬──────────┘  └─────────┬──────────┘
          │                       │                       │
          │                       │                       │
          ▼                       ▼                       ▼

┌──────────────────────────────────────────────────────────────┐
│                     OpenSOC Core Workflow                    │
│--------------------------------------------------------------│
│ Ingestion → Normalisation → Storage → Detection → Alerting   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼

┌──────────────────────────────────────────────────────────────┐
│                    Dashboard & Triage Layer                  │
│--------------------------------------------------------------│
│ Alert Overview • Event Explorer • Incident Timeline          │
│ Severity Views • Validation Outputs                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼

┌──────────────────────────────────────────────────────────────┐
│                     Validation / Lab Layer                   │
│--------------------------------------------------------------│
│ Demo Attack Scenario • Endpoint Testing • Training Use       │
│ Reproducible Exercises • Detection Validation                │
└──────────────────────────────────────────────────────────────┘


Inputs:
- Firewall logs
- Linux events
- Windows events
- System logs

Outputs:
- Alerts
- Dashboards
- Triage workflows
- Reproducible training scenarios
