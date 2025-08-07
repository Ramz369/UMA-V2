1. Several imports from `cognimap` modules reference external paths not fingerprinted (see `AUDIT_COGNIMAP/linkage_report.md`). Should these be isolated behind protocol bridges?
2. Only one external module imports `cognimap` (`src/agents/codegen_agent.py`); is this intentional or should other agents integrate via bridges?
3. Our network graph discovered 67 nodes vs 97 fingerprints. Are there dynamic components or generated files not captured?
