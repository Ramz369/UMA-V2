---
name: sla-verifier
tools: Viewer, Think, Container Runner
soft_cap: 120
trigger: "tag:/use sla-verifier"
---
Run PromQL queries inside container; fail task if thresholds breached.