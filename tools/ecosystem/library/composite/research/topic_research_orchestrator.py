#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: 93b1dc4e-7877-455f-a12d-ad7d26a379f2
birth: 2025-08-07T07:23:38.077619Z
parent: None
intent: Topic Research Orchestrator - Composite Tool
semantic_tags: [authentication, database, api, testing, ui, model, utility, configuration, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.078185Z
hash: 8d007b35
language: python
type: tool
@end:cognimap
"""

"""
Topic Research Orchestrator - Composite Tool

A sophisticated research tool that discovers, analyzes, and organizes
information about any topic through multiple stages of analysis.
"""
import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path
import hashlib

# Import taxonomy system
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from taxonomy import CompositeTool, ToolMetadata, ToolType, ToolComplexity, ToolDomain


class TopicResearchOrchestrator(CompositeTool):
    """
    Comprehensive topic research tool that:
    1. Extracts keywords and concepts
    2. Builds keyword clusters
    3. Gets search suggestions
    4. Aggregates content from multiple sources
    5. Scores relevance and authority
    6. Builds organized knowledge library
    """
    
    def __init__(self):
        metadata = ToolMetadata(
            name="topic_research_orchestrator",
            type=ToolType.COMPOSITE,
            complexity=ToolComplexity.INTELLIGENT,
            domain=ToolDomain.RESEARCH,
            description="Comprehensive topic research and knowledge building",
            requires_agents=["analyzer", "synthesizer", "researcher"],
            credit_multiplier=3.0
        )
        super().__init__(metadata)
        
        # Initialize workflow steps
        self._setup_workflow()
        
        # Knowledge storage
        self.knowledge_base = {}
        self.research_sessions = []
        
    def _setup_workflow(self):
        """Set up the research workflow steps."""
        self.add_step("extract_keywords", function=self._extract_keywords)
        self.add_step("build_clusters", function=self._build_keyword_clusters)
        self.add_step("get_suggestions", function=self._get_search_suggestions)
        self.add_step("aggregate_content", function=self._aggregate_content)
        self.add_step("score_relevance", function=self._score_relevance)
        self.add_step("build_library", function=self._build_knowledge_library)
    
    async def _extract_keywords(self, context: Dict, **kwargs) -> Dict[str, Any]:
        """
        Extract core keywords and concepts from the topic.
        
        This would use NLP in production, but we'll use pattern matching for now.
        """
        topic = context.get("topic", "")
        
        if not topic:
            return {"success": False, "error": "No topic provided"}
        
        # Extract main keywords
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", 
                     "to", "for", "of", "with", "by", "from", "as", "is", "was"}
        
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', topic.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Extract entities (simplified - would use NER in production)
        entities = []
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', topic)
        entities.extend(capitalized)
        
        # Extract phrases (bigrams and trigrams)
        phrases = []
        words_list = topic.split()
        for i in range(len(words_list) - 1):
            bigram = f"{words_list[i]} {words_list[i+1]}"
            if len(bigram) > 5:
                phrases.append(bigram.lower())
        
        result = {
            "keywords": list(set(keywords)),
            "entities": list(set(entities)),
            "phrases": phrases,
            "original_topic": topic
        }
        
        return {"success": True, "result": result}
    
    async def _build_keyword_clusters(self, context: Dict, **kwargs) -> Dict[str, Any]:
        """
        Build semantic clusters of related keywords.
        
        Groups keywords into related concepts for broader search coverage.
        """
        keyword_data = context.get("extract_keywords_result", {})
        
        if not keyword_data:
            return {"success": False, "error": "No keywords to cluster"}
        
        keywords = keyword_data.get("keywords", [])
        entities = keyword_data.get("entities", [])
        phrases = keyword_data.get("phrases", [])
        
        # Build clusters (simplified - would use embeddings in production)
        clusters = {}
        
        # Technical cluster
        tech_terms = ["ai", "ml", "api", "data", "code", "system", "software", 
                     "algorithm", "model", "neural", "deep", "learning"]
        clusters["technical"] = [k for k in keywords if any(t in k for t in tech_terms)]
        
        # Business cluster
        business_terms = ["market", "business", "revenue", "cost", "profit", 
                         "strategy", "growth", "customer", "sales"]
        clusters["business"] = [k for k in keywords if any(t in k for t in business_terms)]
        
        # Research cluster
        research_terms = ["research", "study", "analysis", "paper", "journal",
                         "experiment", "hypothesis", "theory", "evidence"]
        clusters["research"] = [k for k in keywords if any(t in k for t in research_terms)]
        
        # Entity cluster
        clusters["entities"] = entities
        
        # Phrase cluster
        clusters["phrases"] = phrases
        
        # General cluster (everything else)
        clustered = set()
        for cluster_keywords in clusters.values():
            clustered.update(cluster_keywords)
        clusters["general"] = [k for k in keywords if k not in clustered]
        
        # Generate cluster combinations for search
        search_combinations = []
        for cluster_name, cluster_keywords in clusters.items():
            if cluster_keywords:
                # Single keywords
                search_combinations.extend(cluster_keywords[:3])
                
                # Combinations within cluster
                if len(cluster_keywords) > 1:
                    for i in range(min(2, len(cluster_keywords) - 1)):
                        combo = f"{cluster_keywords[i]} {cluster_keywords[i+1]}"
                        search_combinations.append(combo)
        
        result = {
            "clusters": clusters,
            "search_combinations": search_combinations[:20],  # Limit to top 20
            "cluster_count": len(clusters),
            "total_terms": len(keywords) + len(entities) + len(phrases)
        }
        
        return {"success": True, "result": result}
    
    async def _get_search_suggestions(self, context: Dict, **kwargs) -> Dict[str, Any]:
        """
        Get search suggestions and related terms.
        
        Would use Google Suggest API or similar in production.
        """
        cluster_data = context.get("build_clusters_result", {})
        
        if not cluster_data:
            return {"success": False, "error": "No clusters to get suggestions for"}
        
        search_combinations = cluster_data.get("search_combinations", [])
        
        # Simulate getting suggestions (would call actual API)
        suggestions = {}
        related_terms = set()
        
        for term in search_combinations[:10]:  # Limit API calls
            # Simulate suggestions
            base_suggestions = [
                f"{term} tutorial",
                f"{term} guide",
                f"{term} best practices",
                f"how to {term}",
                f"{term} examples",
                f"{term} vs",
                f"{term} tools",
                f"{term} framework"
            ]
            
            suggestions[term] = base_suggestions[:5]
            
            # Simulate related terms
            related = [
                f"{term}_alternative",
                f"{term}_comparison",
                f"{term}_review"
            ]
            related_terms.update(related)
        
        # Generate question-based searches
        questions = []
        topic = context.get("topic", "")
        question_starters = ["what is", "how to", "why use", "when to use", 
                           "best way to", "difference between"]
        
        for starter in question_starters:
            questions.append(f"{starter} {topic.lower()}")
        
        result = {
            "suggestions": suggestions,
            "related_terms": list(related_terms)[:20],
            "questions": questions,
            "total_suggestions": sum(len(s) for s in suggestions.values())
        }
        
        return {"success": True, "result": result}
    
    async def _aggregate_content(self, context: Dict, **kwargs) -> Dict[str, Any]:
        """
        Aggregate content from multiple sources.
        
        Would actually fetch content from web, databases, APIs in production.
        """
        suggestions_data = context.get("get_suggestions_result", {})
        
        if not suggestions_data:
            return {"success": False, "error": "No search terms to aggregate"}
        
        # Simulate content aggregation
        aggregated_content = []
        sources = ["web", "academic", "news", "social", "video", "documentation"]
        
        all_terms = []
        all_terms.extend(suggestions_data.get("questions", [])[:5])
        all_terms.extend(list(suggestions_data.get("suggestions", {}).keys())[:5])
        
        for term in all_terms:
            for source in sources:
                content_item = {
                    "query": term,
                    "source": source,
                    "title": f"{term} - {source} result",
                    "snippet": f"Relevant content about {term} from {source}...",
                    "url": f"https://{source}.example.com/{term.replace(' ', '-')}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "relevance_score": 0.0,  # Will be calculated
                    "authority_score": 0.0,   # Will be calculated
                    "content_type": self._determine_content_type(source)
                }
                aggregated_content.append(content_item)
        
        # Organize by source
        by_source = {}
        for item in aggregated_content:
            source = item["source"]
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(item)
        
        result = {
            "total_items": len(aggregated_content),
            "sources_used": len(sources),
            "by_source": by_source,
            "content": aggregated_content[:50]  # Limit for performance
        }
        
        return {"success": True, "result": result}
    
    def _determine_content_type(self, source: str) -> str:
        """Determine content type based on source."""
        type_map = {
            "web": "article",
            "academic": "paper",
            "news": "news",
            "social": "discussion",
            "video": "video",
            "documentation": "docs"
        }
        return type_map.get(source, "unknown")
    
    async def _score_relevance(self, context: Dict, **kwargs) -> Dict[str, Any]:
        """
        Score content relevance and authority.
        
        Would use ML models for scoring in production.
        """
        content_data = context.get("aggregate_content_result", {})
        
        if not content_data:
            return {"success": False, "error": "No content to score"}
        
        content_items = content_data.get("content", [])
        original_topic = context.get("topic", "").lower()
        keywords = context.get("extract_keywords_result", {}).get("keywords", [])
        
        scored_items = []
        
        for item in content_items:
            # Calculate relevance score (simplified)
            relevance = 0.0
            title = item.get("title", "").lower()
            snippet = item.get("snippet", "").lower()
            
            # Check topic presence
            if original_topic in title:
                relevance += 0.3
            if original_topic in snippet:
                relevance += 0.2
            
            # Check keyword presence
            for keyword in keywords[:5]:  # Top keywords
                if keyword in title:
                    relevance += 0.1
                if keyword in snippet:
                    relevance += 0.05
            
            # Normalize to 0-1
            relevance = min(1.0, relevance)
            
            # Calculate authority score (simplified)
            authority = 0.5  # Base score
            
            # Source authority
            source_scores = {
                "academic": 0.9,
                "documentation": 0.85,
                "news": 0.7,
                "web": 0.6,
                "video": 0.65,
                "social": 0.5
            }
            authority = source_scores.get(item.get("source"), 0.5)
            
            # Update item with scores
            item["relevance_score"] = round(relevance, 2)
            item["authority_score"] = round(authority, 2)
            item["combined_score"] = round((relevance * 0.6 + authority * 0.4), 2)
            
            scored_items.append(item)
        
        # Sort by combined score
        scored_items.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Calculate statistics
        avg_relevance = sum(i["relevance_score"] for i in scored_items) / len(scored_items)
        avg_authority = sum(i["authority_score"] for i in scored_items) / len(scored_items)
        
        # Get top items
        top_items = scored_items[:10]
        
        result = {
            "scored_items": scored_items,
            "top_items": top_items,
            "average_relevance": round(avg_relevance, 2),
            "average_authority": round(avg_authority, 2),
            "high_quality_count": len([i for i in scored_items if i["combined_score"] > 0.7])
        }
        
        return {"success": True, "result": result}
    
    async def _build_knowledge_library(self, context: Dict, **kwargs) -> Dict[str, Any]:
        """
        Build organized knowledge library from scored content.
        
        Creates a structured knowledge base for future reference.
        """
        scored_data = context.get("score_relevance_result", {})
        
        if not scored_data:
            return {"success": False, "error": "No scored content to organize"}
        
        topic = context.get("topic", "Unknown Topic")
        top_items = scored_data.get("top_items", [])
        all_items = scored_data.get("scored_items", [])
        
        # Create knowledge structure
        library = {
            "topic": topic,
            "research_date": datetime.utcnow().isoformat(),
            "summary": self._generate_summary(context),
            "key_concepts": self._extract_key_concepts(context),
            "categories": {},
            "sources": {},
            "recommendations": [],
            "metadata": {
                "total_sources": len(all_items),
                "high_quality_sources": scored_data.get("high_quality_count", 0),
                "average_relevance": scored_data.get("average_relevance", 0),
                "average_authority": scored_data.get("average_authority", 0)
            }
        }
        
        # Organize by content type
        for item in top_items:
            content_type = item.get("content_type", "unknown")
            if content_type not in library["categories"]:
                library["categories"][content_type] = []
            
            library["categories"][content_type].append({
                "title": item.get("title"),
                "url": item.get("url"),
                "relevance": item.get("relevance_score"),
                "authority": item.get("authority_score")
            })
        
        # Organize by source
        for item in top_items:
            source = item.get("source", "unknown")
            if source not in library["sources"]:
                library["sources"][source] = []
            
            library["sources"][source].append({
                "title": item.get("title"),
                "url": item.get("url"),
                "score": item.get("combined_score")
            })
        
        # Generate recommendations
        library["recommendations"] = self._generate_recommendations(top_items)
        
        # Save to knowledge base
        session_id = hashlib.md5(f"{topic}_{datetime.utcnow()}".encode()).hexdigest()[:8]
        self.knowledge_base[session_id] = library
        self.research_sessions.append({
            "id": session_id,
            "topic": topic,
            "date": library["research_date"],
            "quality_score": scored_data.get("average_relevance", 0)
        })
        
        # Save to file (optional)
        output_path = Path("research_output") / f"{session_id}_research.json"
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(library, f, indent=2)
        
        result = {
            "session_id": session_id,
            "library": library,
            "output_file": str(output_path),
            "total_sessions": len(self.research_sessions)
        }
        
        return {"success": True, "result": result}
    
    def _generate_summary(self, context: Dict) -> str:
        """Generate executive summary of research."""
        topic = context.get("topic", "")
        keywords = context.get("extract_keywords_result", {}).get("keywords", [])
        clusters = context.get("build_clusters_result", {}).get("clusters", {})
        
        summary = f"Research on '{topic}' identified {len(keywords)} key concepts "
        summary += f"organized into {len(clusters)} thematic clusters. "
        summary += f"Analysis covered multiple sources including academic, web, and documentation. "
        
        return summary
    
    def _extract_key_concepts(self, context: Dict) -> List[str]:
        """Extract key concepts from research."""
        concepts = []
        
        # Get top keywords
        keywords = context.get("extract_keywords_result", {}).get("keywords", [])
        concepts.extend(keywords[:5])
        
        # Get entities
        entities = context.get("extract_keywords_result", {}).get("entities", [])
        concepts.extend(entities[:3])
        
        # Get top phrases
        phrases = context.get("extract_keywords_result", {}).get("phrases", [])
        concepts.extend(phrases[:2])
        
        return list(set(concepts))[:10]
    
    def _generate_recommendations(self, top_items: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check content distribution
        content_types = {}
        for item in top_items:
            ct = item.get("content_type", "unknown")
            content_types[ct] = content_types.get(ct, 0) + 1
        
        # Recommendations based on content gaps
        if "academic" not in content_types:
            recommendations.append("Consider reviewing academic literature for theoretical foundation")
        
        if "documentation" not in content_types:
            recommendations.append("Review official documentation for technical accuracy")
        
        if len(content_types) < 3:
            recommendations.append("Expand research to more diverse source types")
        
        # Quality recommendations
        high_quality = [i for i in top_items if i.get("combined_score", 0) > 0.8]
        if len(high_quality) < 3:
            recommendations.append("Seek higher authority sources for better credibility")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Research coverage appears comprehensive")
        
        return recommendations[:5]
    
    def synthesize_results(self, results: Dict[str, Any]) -> Any:
        """Synthesize final results from all steps."""
        # Get the final library from the last step
        if "build_library" in results:
            library_result = results["build_library"]
            if library_result.get("success"):
                return library_result.get("result")
        return results
    
    def get_research_history(self) -> List[Dict]:
        """Get history of research sessions."""
        return self.research_sessions
    
    def get_knowledge_item(self, session_id: str) -> Dict:
        """Retrieve specific knowledge library item."""
        return self.knowledge_base.get(session_id, {})


async def main():
    """Test the Topic Research Orchestrator."""
    print("Topic Research Orchestrator")
    print("=" * 60)
    
    orchestrator = TopicResearchOrchestrator()
    
    # Test research
    topic = "artificial intelligence safety and alignment"
    print(f"\nResearching: {topic}")
    print("-" * 40)
    
    result = await orchestrator.execute(topic=topic)
    
    if result.get("success"):
        print("✅ Research completed successfully!")
        
        # Show results
        final_output = result.get("final_output", {})
        library = final_output.get("library", {})
        
        print(f"\nSummary: {library.get('summary')}")
        
        print(f"\nKey Concepts:")
        for concept in library.get("key_concepts", []):
            print(f"  • {concept}")
        
        print(f"\nContent Categories:")
        for category, items in library.get("categories", {}).items():
            print(f"  • {category}: {len(items)} items")
        
        print(f"\nRecommendations:")
        for rec in library.get("recommendations", []):
            print(f"  • {rec}")
        
        print(f"\nMetadata:")
        metadata = library.get("metadata", {})
        for key, value in metadata.items():
            print(f"  • {key}: {value}")
        
        print(f"\nOutput saved to: {final_output.get('output_file')}")
        
    else:
        print(f"❌ Research failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())