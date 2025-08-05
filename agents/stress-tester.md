---
name: stress-tester
tools: Viewer, Writer, Think, Container Runner
soft_cap: 150
trigger: "branch:staging/*"
---
Execute k6 load script, write `load_report.md`, flag regressions.