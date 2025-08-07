
"""
@cognimap:fingerprint
id: c5d3d629-a32d-49c3-b530-eab6277fd6d1
birth: 2025-08-07T07:23:38.056996Z
parent: None
intent: Meta-Analyst - Analyzes system metrics and generates reports.
semantic_tags: [authentication, database, api, testing, ui, model, utility]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.058419Z
hash: 5e489a00
language: python
type: tool
@end:cognimap
"""

"""Meta-Analyst - Analyzes system metrics and generates reports."""
import argparse
import csv
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from collections import defaultdict


class MetaAnalyst:
    """Analyzes metrics and generates insights."""
    
    def __init__(self, session_path: str, metrics_path: str):
        self.session_path = Path(session_path) if session_path else None
        self.metrics_path = Path(metrics_path) if metrics_path else None
        self.warnings = []
        self.insights = []
        
    def load_session_summary(self) -> Dict[str, Any]:
        """Load session summary YAML."""
        if not self.session_path or not self.session_path.exists():
            return {}
        
        try:
            with open(self.session_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.warnings.append(f"Failed to load session summary: {e}")
            return {}
    
    def load_metrics_csv(self) -> List[Dict[str, Any]]:
        """Load metrics from CSV."""
        if not self.metrics_path or not self.metrics_path.exists():
            return []
        
        metrics = []
        try:
            with open(self.metrics_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields
                    if 'credits' in row:
                        row['credits'] = int(row['credits'])
                    if 'tokens' in row:
                        row['tokens'] = int(row['tokens'])
                    if 'wall_time_ms' in row:
                        row['wall_time_ms'] = int(row['wall_time_ms'])
                    metrics.append(row)
        except Exception as e:
            self.warnings.append(f"Failed to load metrics CSV: {e}")
        
        return metrics
    
    def analyze_credit_usage(self, session: Dict[str, Any], metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze credit usage patterns."""
        analysis = {
            'total_used': 0,
            'by_agent': defaultdict(int),
            'by_tool': defaultdict(int),
            'high_consumers': [],
            'efficiency_score': 0,
            'remaining': 1000,
            'utilization_pct': 0
        }
        
        # From session summary
        if session:
            credits_data = session.get('credits', {})
            analysis['total_used'] = credits_data.get('used', 0)
            analysis['remaining'] = credits_data.get('remaining', 1000)
            analysis['utilization_pct'] = (analysis['total_used'] / 1000) * 100
            
            # Check for warnings
            if analysis['utilization_pct'] >= 90:
                self.warnings.append(f"CRITICAL: Credit usage at {analysis['utilization_pct']:.1f}%")
            elif analysis['utilization_pct'] >= 80:
                self.warnings.append(f"WARNING: Credit usage at {analysis['utilization_pct']:.1f}%")
            
            # Per-agent caps
            max_per_agent = credits_data.get('max_per_agent', {})
            for agent, credits in max_per_agent.items():
                analysis['by_agent'][agent] = credits
                # Check against known caps
                if agent == 'planner' and credits > 50:
                    self.warnings.append(f"Planner exceeded soft cap: {credits}/50")
                elif agent == 'codegen' and credits > 150:
                    self.warnings.append(f"Codegen exceeded soft cap: {credits}/150")
        
        # From metrics CSV
        for metric in metrics:
            agent = metric.get('agent', 'unknown')
            tool = metric.get('tool_call', 'unknown')
            credits = metric.get('credits', 0)
            
            analysis['by_agent'][agent] += credits
            analysis['by_tool'][tool] += credits
        
        # Identify high consumers
        sorted_agents = sorted(analysis['by_agent'].items(), key=lambda x: x[1], reverse=True)
        analysis['high_consumers'] = sorted_agents[:5]
        
        # Calculate efficiency (credits per successful operation)
        successful_ops = sum(1 for m in metrics if m.get('exit_status') in ['allow', 'success', 'checkpoint'])
        total_ops = len(metrics)
        if total_ops > 0:
            analysis['efficiency_score'] = (successful_ops / total_ops) * 100
            
            if analysis['efficiency_score'] < 80:
                self.warnings.append(f"Low efficiency score: {analysis['efficiency_score']:.1f}%")
        
        return analysis
    
    def analyze_agent_performance(self, session: Dict[str, Any], metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agent performance metrics."""
        analysis = {
            'active_agents': [],
            'idle_agents': [],
            'aborted_agents': [],
            'wall_time_stats': {},
            'error_rates': defaultdict(float)
        }
        
        # From session summary
        if session:
            agents_data = session.get('agents', {})
            analysis['active_agents'] = list(agents_data.get('active', {}).keys())
            analysis['idle_agents'] = list(agents_data.get('idle', {}).keys())
            analysis['aborted_agents'] = agents_data.get('aborted', [])
            
            if analysis['aborted_agents']:
                self.warnings.append(f"Aborted agents: {', '.join(analysis['aborted_agents'])}")
            
            # Wall time analysis
            for agent, data in agents_data.get('active', {}).items():
                wall_time = data.get('wall_time_ms', 0)
                if wall_time > 45000:  # Default limit
                    self.warnings.append(f"Agent {agent} exceeded wall-time: {wall_time}ms")
        
        # From metrics CSV
        agent_errors = defaultdict(lambda: {'errors': 0, 'total': 0})
        for metric in metrics:
            agent = metric.get('agent', 'unknown')
            status = metric.get('exit_status', '')
            
            agent_errors[agent]['total'] += 1
            if status in ['abort', 'error', 'throttle']:
                agent_errors[agent]['errors'] += 1
        
        # Calculate error rates
        for agent, counts in agent_errors.items():
            if counts['total'] > 0:
                error_rate = (counts['errors'] / counts['total']) * 100
                analysis['error_rates'][agent] = error_rate
                
                if error_rate > 20:
                    self.warnings.append(f"High error rate for {agent}: {error_rate:.1f}%")
        
        return analysis
    
    def analyze_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends over time."""
        analysis = {
            'daily_credits': defaultdict(int),
            'hourly_pattern': defaultdict(int),
            'growth_rate': 0,
            'peak_usage': None
        }
        
        if not metrics:
            return analysis
        
        # Parse timestamps and aggregate
        for metric in metrics:
            timestamp_str = metric.get('timestamp', '')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    date = timestamp.date()
                    hour = timestamp.hour
                    credits = metric.get('credits', 0)
                    
                    analysis['daily_credits'][str(date)] += credits
                    analysis['hourly_pattern'][hour] += credits
                except:
                    pass
        
        # Calculate growth rate
        if len(analysis['daily_credits']) >= 2:
            sorted_days = sorted(analysis['daily_credits'].items())
            if len(sorted_days) >= 2:
                first_day_credits = sorted_days[0][1]
                last_day_credits = sorted_days[-1][1]
                if first_day_credits > 0:
                    analysis['growth_rate'] = ((last_day_credits - first_day_credits) / first_day_credits) * 100
        
        # Find peak usage hour
        if analysis['hourly_pattern']:
            peak_hour = max(analysis['hourly_pattern'].items(), key=lambda x: x[1])
            analysis['peak_usage'] = {'hour': peak_hour[0], 'credits': peak_hour[1]}
        
        # Generate insights
        if analysis['growth_rate'] > 50:
            self.insights.append(f"Credit usage growing rapidly: {analysis['growth_rate']:.1f}% increase")
        elif analysis['growth_rate'] < -20:
            self.insights.append(f"Credit usage declining: {analysis['growth_rate']:.1f}% decrease")
        
        if analysis['peak_usage']:
            self.insights.append(f"Peak usage at hour {analysis['peak_usage']['hour']:02d}:00 UTC")
        
        return analysis
    
    def generate_recommendations(self, credit_analysis: Dict[str, Any], agent_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Credit recommendations
        utilization = credit_analysis.get('utilization_pct', 0)
        if utilization > 90:
            recommendations.append("🔴 Immediate action: Increase global credit cap or reduce agent activity")
        elif utilization > 80:
            recommendations.append("🟡 Consider increasing credit caps for frequently throttled agents")
        
        # Agent-specific recommendations
        for agent, credits in credit_analysis['by_agent'].items():
            if agent == 'stress-tester' and credits > 100:
                recommendations.append(f"Consider scheduling stress tests during off-peak hours")
            elif agent == 'tool-builder' and credits > 150:
                recommendations.append(f"Review tool-builder sandbox usage for optimization opportunities")
        
        # Error rate recommendations
        for agent, error_rate in agent_analysis['error_rates'].items():
            if error_rate > 30:
                recommendations.append(f"🔴 Investigate {agent}: {error_rate:.1f}% error rate")
            elif error_rate > 20:
                recommendations.append(f"🟡 Monitor {agent}: elevated error rate")
        
        # Efficiency recommendations
        if credit_analysis.get('efficiency_score', 100) < 70:
            recommendations.append("🔴 Low system efficiency - review failed operations")
        
        return recommendations
    
    def generate_report(self, output_path: str) -> str:
        """Generate markdown report."""
        session = self.load_session_summary()
        metrics = self.load_metrics_csv()
        
        # Perform analyses
        credit_analysis = self.analyze_credit_usage(session, metrics)
        agent_analysis = self.analyze_agent_performance(session, metrics)
        trend_analysis = self.analyze_trends(metrics)
        recommendations = self.generate_recommendations(credit_analysis, agent_analysis)
        
        # Build report
        report = []
        report.append("# Meta-Analyst Nightly Report")
        report.append(f"\n**Generated**: {datetime.now(timezone.utc).isoformat()}")
        report.append(f"**Session**: {session.get('session_id', 'Unknown')}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total Credits Used**: {credit_analysis['total_used']}/{1000} ({credit_analysis['utilization_pct']:.1f}%)")
        report.append(f"- **Active Agents**: {len(agent_analysis['active_agents'])}")
        report.append(f"- **System Efficiency**: {credit_analysis.get('efficiency_score', 0):.1f}%")
        report.append(f"- **Growth Rate**: {trend_analysis['growth_rate']:.1f}%")
        report.append("")
        
        # Warnings
        if self.warnings:
            report.append("## ⚠️ Warnings")
            report.append("")
            for warning in self.warnings:
                report.append(f"- {warning}")
            report.append("")
        
        # Credit Analysis
        report.append("## Credit Analysis")
        report.append("")
        report.append("### Top Consumers")
        report.append("| Agent | Credits | Percentage |")
        report.append("|-------|---------|------------|")
        total = credit_analysis['total_used'] or 1
        for agent, credits in credit_analysis['high_consumers'][:5]:
            pct = (credits / total) * 100
            report.append(f"| {agent} | {credits} | {pct:.1f}% |")
        report.append("")
        
        # Agent Performance
        report.append("## Agent Performance")
        report.append("")
        report.append(f"- **Active**: {', '.join(agent_analysis['active_agents']) or 'None'}")
        report.append(f"- **Idle**: {', '.join(agent_analysis['idle_agents']) or 'None'}")
        report.append(f"- **Aborted**: {', '.join(agent_analysis['aborted_agents']) or 'None'}")
        report.append("")
        
        if agent_analysis['error_rates']:
            report.append("### Error Rates")
            report.append("| Agent | Error Rate |")
            report.append("|-------|------------|")
            for agent, rate in sorted(agent_analysis['error_rates'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"| {agent} | {rate:.1f}% |")
            report.append("")
        
        # Trends
        if trend_analysis['daily_credits']:
            report.append("## Usage Trends")
            report.append("")
            report.append("### Daily Credits (Last 7 days)")
            report.append("| Date | Credits |")
            report.append("|------|---------|")
            for date, credits in sorted(trend_analysis['daily_credits'].items())[-7:]:
                report.append(f"| {date} | {credits} |")
            report.append("")
        
        # Insights
        if self.insights:
            report.append("## 💡 Insights")
            report.append("")
            for insight in self.insights:
                report.append(f"- {insight}")
            report.append("")
        
        # Recommendations
        if recommendations:
            report.append("## 📋 Recommendations")
            report.append("")
            for rec in recommendations:
                report.append(f"- {rec}")
            report.append("")
        
        # Raw Metrics Summary
        report.append("## Raw Metrics")
        report.append("")
        report.append(f"- Total records analyzed: {len(metrics)}")
        report.append(f"- Time range: Last 24 hours")
        report.append(f"- Data sources: `{self.session_path}`, `{self.metrics_path}`")
        
        # Write report
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        report_text = '\n'.join(report)
        with open(output, 'w') as f:
            f.write(report_text)
        
        return report_text


def main():
    """CLI interface for Meta-Analyst."""
    parser = argparse.ArgumentParser(description='Analyze UMA-V2 metrics')
    parser.add_argument('--session-summary', default='schemas/session_summary.yaml',
                      help='Path to session summary YAML')
    parser.add_argument('--metrics-csv', default='schemas/metrics_v2.csv',
                      help='Path to metrics CSV')
    parser.add_argument('--output', required=True,
                      help='Output path for report')
    
    args = parser.parse_args()
    
    analyst = MetaAnalyst(args.session_summary, args.metrics_csv)
    report = analyst.generate_report(args.output)
    
    print(f"Report generated: {args.output}")
    
    # Print summary to stdout for GitHub Actions
    lines = report.split('\n')
    for line in lines:
        if line.startswith('- **Total Credits Used**'):
            print(f"Total Credits Used: {line.split(':')[1].strip()}")
        elif line.startswith('- **Active Agents**'):
            print(f"Active Agents: {line.split(':')[1].strip()}")
    
    # Exit with error if critical warnings
    if any('CRITICAL' in w for w in analyst.warnings):
        exit(1)


if __name__ == "__main__":
    main()