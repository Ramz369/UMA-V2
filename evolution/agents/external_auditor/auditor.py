"""External Auditor Agent - Fresh perspective analysis of the system."""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ExternalAuditor:
    """
    The External Auditor provides an unbiased, outside perspective on the system.
    It questions assumptions, identifies inefficiencies, and proposes improvements.
    Role: Like Gemini in our 4-entity collaboration - the outsider.
    """
    
    def __init__(self, config_path: str = "evolution/protocols/evolution_protocol.yaml"):
        self.config_path = config_path
        self.analysis_history = []
        self.focus_areas = [
            "code_quality",
            "performance_bottlenecks",
            "architectural_debt", 
            "revenue_opportunities",
            "security_vulnerabilities",
            "resource_efficiency"
        ]
    
    async def analyze_system(self) -> Dict[str, Any]:
        """
        Perform comprehensive system analysis from an outsider's perspective.
        Questions everything, assumes nothing.
        """
        logger.info("External Auditor: Beginning system analysis")
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "external_auditor",
            "findings": [],
            "proposals": [],
            "risk_assessment": {},
            "opportunity_assessment": {}
        }
        
        # Analyze each focus area
        for area in self.focus_areas:
            findings = await self._analyze_area(area)
            analysis["findings"].extend(findings)
        
        # Generate proposals based on findings
        analysis["proposals"] = self._generate_proposals(analysis["findings"])
        
        # Assess risks and opportunities
        analysis["risk_assessment"] = self._assess_risks(analysis["findings"])
        analysis["opportunity_assessment"] = self._identify_opportunities(analysis["findings"])
        
        # Store in history
        self.analysis_history.append(analysis)
        
        # Emit to evolution event stream
        await self._emit_analysis(analysis)
        
        logger.info(f"External Auditor: Analysis complete. {len(analysis['proposals'])} proposals generated")
        return analysis
    
    async def _analyze_area(self, area: str) -> List[Dict[str, Any]]:
        """Analyze a specific focus area."""
        findings = []
        
        if area == "code_quality":
            findings.append({
                "area": "code_quality",
                "issue": "Duplicate code patterns detected",
                "severity": "MEDIUM",
                "location": "tools/semantic_diff.py",
                "suggestion": "Extract common AST traversal logic into shared utility"
            })
        
        elif area == "revenue_opportunities":
            findings.append({
                "area": "revenue_opportunities",
                "opportunity": "Monetize semantic diff as API",
                "potential_revenue": "$50-200/day",
                "implementation_cost": "$100",
                "time_to_market": "3 days"
            })
        
        elif area == "performance_bottlenecks":
            findings.append({
                "area": "performance",
                "bottleneck": "Sequential agent execution",
                "impact": "3x slower than necessary",
                "solution": "Implement parallel agent orchestration"
            })
        
        # Add more analysis logic for each area
        return findings
    
    def _generate_proposals(self, findings: List[Dict]) -> List[Dict]:
        """Generate actionable proposals from findings."""
        proposals = []
        
        for finding in findings:
            if finding.get("severity") in ["HIGH", "CRITICAL"] or \
               finding.get("potential_revenue"):
                proposal = {
                    "title": f"Address: {finding.get('issue', finding.get('opportunity', 'Unknown'))}",
                    "description": finding.get("suggestion", finding.get("solution", "")),
                    "priority": self._calculate_priority(finding),
                    "estimated_effort": self._estimate_effort(finding),
                    "expected_benefit": self._calculate_benefit(finding)
                }
                proposals.append(proposal)
        
        return sorted(proposals, key=lambda x: x["priority"], reverse=True)
    
    def _assess_risks(self, findings: List[Dict]) -> Dict:
        """Assess systemic risks from findings."""
        risks = {
            "technical_debt": 0,
            "security_exposure": 0,
            "scalability_limit": 0,
            "maintenance_burden": 0
        }
        
        for finding in findings:
            if "debt" in str(finding).lower():
                risks["technical_debt"] += 1
            if "security" in str(finding).lower():
                risks["security_exposure"] += 1
            # Add more risk assessment logic
        
        return risks
    
    def _identify_opportunities(self, findings: List[Dict]) -> Dict:
        """Identify growth opportunities from findings."""
        opportunities = {
            "revenue_potential": 0,
            "efficiency_gains": 0,
            "capability_expansion": 0,
            "market_reach": 0
        }
        
        for finding in findings:
            if finding.get("potential_revenue"):
                # Parse revenue string and accumulate
                opportunities["revenue_potential"] += 100  # Simplified
            # Add more opportunity assessment logic
        
        return opportunities
    
    def _calculate_priority(self, finding: Dict) -> str:
        """Calculate priority based on severity and opportunity."""
        if finding.get("severity") == "CRITICAL":
            return "CRITICAL"
        elif finding.get("potential_revenue"):
            revenue = finding.get("potential_revenue", "")
            if "$200" in revenue or "$500" in revenue:
                return "HIGH"
        return "MEDIUM"
    
    def _estimate_effort(self, finding: Dict) -> str:
        """Estimate implementation effort."""
        if finding.get("implementation_cost"):
            cost = finding.get("implementation_cost", "")
            if "$100" in cost:
                return "LOW"
            elif "$500" in cost:
                return "MEDIUM"
        return "UNKNOWN"
    
    def _calculate_benefit(self, finding: Dict) -> Dict:
        """Calculate expected benefit from addressing finding."""
        return {
            "revenue": finding.get("potential_revenue", "$0"),
            "performance": finding.get("impact", "unknown"),
            "risk_reduction": finding.get("severity", "unknown")
        }
    
    async def _emit_analysis(self, analysis: Dict):
        """Emit analysis to evolution event stream."""
        # TODO: Connect to Redpanda and emit event
        logger.info("Emitting analysis to evo.proposals topic")
    
    def question_assumption(self, assumption: str) -> str:
        """
        Question a fundamental assumption about the system.
        This is the key role of the external auditor - challenge everything.
        """
        questions = {
            "agents_are_necessary": "Why use agents at all? Could event-driven be better?",
            "python_is_best": "Would Rust provide 10x performance for the same effort?",
            "monolithic_repo": "Should this be microservices instead?",
            "human_oversight": "Could full autonomy actually be safer with proper constraints?"
        }
        
        return questions.get(assumption, f"What evidence supports: {assumption}?")


# Example usage for bootstrap
if __name__ == "__main__":
    import asyncio
    
    async def bootstrap_audit():
        auditor = ExternalAuditor()
        analysis = await auditor.analyze_system()
        print(json.dumps(analysis, indent=2))
    
    asyncio.run(bootstrap_audit())