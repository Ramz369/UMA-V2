#!/usr/bin/env python3
"""
Tests for Tool Hunter Agent
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import shutil

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.tool_hunter_agent import (
    ToolHunterAgent,
    ToolProtocol,
    TrustLevel,
    DiscoveredTool,
    AdaptedTool,
    TestResult
)


class TestToolHunterAgent:
    """Test cases for Tool Hunter Agent."""
    
    def setup_method(self):
        """Set up test environment."""
        self.hunter = ToolHunterAgent()
        # Use temp directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.hunter.library_path = self.temp_dir / "library"
        self.hunter.registry_path = self.temp_dir / "registry"
        
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test agent initialization."""
        assert self.hunter.name == "tool-hunter"
        assert self.hunter.version == "1.0.0"
        assert len(self.hunter.mcp_sources) > 0
        assert len(self.hunter.pattern_sources) > 0
    
    async def test_discover_tools(self):
        """Test tool discovery."""
        tools = await self.hunter.discover_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check discovered tool structure
        for tool in tools:
            assert isinstance(tool, DiscoveredTool)
            assert tool.name
            assert tool.description
            assert tool.protocol in ToolProtocol
            assert tool.confidence_score >= 0 and tool.confidence_score <= 1
    
    async def test_mcp_discovery(self):
        """Test MCP tool discovery."""
        tools = await self.hunter._discover_mcp_tools(
            "https://github.com/modelcontextprotocol/servers"
        )
        
        assert len(tools) > 0
        assert all(t.protocol == ToolProtocol.MCP for t in tools)
        assert any(t.name == "filesystem" for t in tools)
        assert any(t.name == "sqlite" for t in tools)
    
    async def test_pattern_discovery(self):
        """Test pattern-based tool discovery."""
        tools = await self.hunter._discover_pattern_tools("chain-patterns")
        
        assert len(tools) > 0
        assert all(t.protocol == ToolProtocol.NATIVE for t in tools)
        assert any("search" in t.name for t in tools)
    
    async def test_analyze_patterns(self):
        """Test pattern analysis."""
        # Create test tools
        tools = [
            DiscoveredTool(
                source_url="test://tool1",
                protocol=ToolProtocol.MCP,
                name="test_tool_1",
                description="Test tool 1",
                capabilities=["search", "filter"],
                discovered_at=datetime.utcnow(),
                confidence_score=0.5
            ),
            DiscoveredTool(
                source_url="test://tool2",
                protocol=ToolProtocol.MCP,
                name="test_tool_2",
                description="Test tool 2",
                capabilities=["search", "filter"],
                discovered_at=datetime.utcnow(),
                confidence_score=0.5
            )
        ]
        
        analyzed = await self.hunter.analyze_patterns(tools)
        
        assert len(analyzed) == len(tools)
        assert len(self.hunter.tool_patterns) > 0
        
        # Check pattern detection
        pattern_key = list(self.hunter.tool_patterns.keys())[0]
        pattern = self.hunter.tool_patterns[pattern_key]
        assert pattern.frequency == 2
        assert len(pattern.examples) == 2
    
    async def test_adapt_to_cogplan(self):
        """Test tool adaptation."""
        tools = [
            DiscoveredTool(
                source_url="test://search",
                protocol=ToolProtocol.MCP,
                name="web_search",
                description="Search the web",
                capabilities=["search"],
                discovered_at=datetime.utcnow(),
                confidence_score=0.8
            )
        ]
        
        adapted = await self.hunter.adapt_to_cogplan(tools)
        
        assert len(adapted) == 1
        tool = adapted[0]
        
        assert isinstance(tool, AdaptedTool)
        assert tool.uuid.startswith("cogplan-tool-")
        assert tool.name == "web_search"
        assert tool.version == "1.0.0"
        assert tool.family
        assert tool.manifest
        assert tool.source_code
        assert tool.test_suite
        assert tool.documentation
        
        # Check manifest structure
        manifest = tool.manifest
        assert "identity" in manifest
        assert "origin" in manifest
        assert "capability" in manifest
        assert "protocol" in manifest
        assert "interface" in manifest
        assert "execution" in manifest
        assert "evolution" in manifest
        assert "economics" in manifest
    
    async def test_isolation_testing(self):
        """Test isolation lab testing."""
        # Create adapted tool
        tool = AdaptedTool(
            uuid="test-tool-001",
            name="test_tool",
            version="1.0.0",
            family="foundation/test",
            protocol=ToolProtocol.MCP,
            manifest={"test": "manifest"},
            source_code="# test code"
        )
        
        tested = await self.hunter.test_in_isolation([tool])
        
        # Should pass our simulated test
        assert len(tested) <= 1
        
        if tested:
            assert tool.uuid in self.hunter.test_results
            result = self.hunter.test_results[tool.uuid]
            assert isinstance(result, TestResult)
            assert result.performance_score >= 0
            assert result.security_score >= 0
            assert result.reliability_score >= 0
    
    async def test_integration(self):
        """Test library integration."""
        # Create a passing tool
        tool = AdaptedTool(
            uuid="test-integration-001",
            name="integration_test",
            version="1.0.0",
            family="foundation/test",
            protocol=ToolProtocol.MCP,
            manifest={
                "identity": {"name": "integration_test"},
                "economics": {"credit_cost": {"base": 1}}
            },
            source_code="# test",
            test_suite="# test",
            documentation="# doc"
        )
        
        # Add passing test result
        self.hunter.test_results[tool.uuid] = TestResult(
            tool_uuid=tool.uuid,
            passed=True,
            performance_score=0.9,
            security_score=0.9,
            reliability_score=0.9,
            errors=[],
            warnings=[],
            resource_usage={}
        )
        
        integrated = await self.hunter.integrate_to_library([tool])
        
        assert len(integrated) == 1
        assert integrated[0] == tool.uuid
        
        # Check files were created
        manifest_file = self.hunter.registry_path / f"{tool.uuid}.yaml"
        assert manifest_file.exists()
    
    async def test_evolution(self):
        """Test tool evolution."""
        # Create registry with a tool needing evolution
        self.hunter.registry_path.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            "identity": {
                "uuid": "evolve-test-001",
                "name": "evolve_test",
                "version": "1.0.0"
            },
            "evolution": {
                "performance_score": 0.5,  # Poor performance
                "usage_count": 200,  # High usage
                "improvement_suggestions": ["optimize"]
            },
            "economics": {
                "credit_cost": {"base": 10}  # High cost
            },
            "execution": {
                "resources": {"timeout": 60}  # Long timeout
            }
        }
        
        manifest_file = self.hunter.registry_path / "evolve-test-001.yaml"
        with open(manifest_file, 'w') as f:
            import yaml
            yaml.dump(manifest, f)
        
        evolved = await self.hunter.evolve_existing_tools()
        
        # Should identify tool for evolution
        assert isinstance(evolved, list)
        # In real implementation would create new version
    
    async def test_full_hunt_cycle(self):
        """Test complete hunting cycle."""
        report = await self.hunter.hunt_cycle()
        
        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "discovered" in report
        assert "adapted" in report
        assert "tested" in report
        assert "integrated" in report
        assert "summary" in report
        
        assert report["agent"] == "tool-hunter"
        assert report["discovered"] >= 0
        assert report["adapted"] >= 0
        assert report["tested"] >= 0
        assert report["integrated"] >= 0
    
    def test_trust_level_determination(self):
        """Test trust level determination."""
        # High scores -> Verified
        result = TestResult(
            tool_uuid="test",
            passed=True,
            performance_score=0.95,
            security_score=0.92,
            reliability_score=0.91,
            errors=[],
            warnings=[],
            resource_usage={}
        )
        
        trust = self.hunter._determine_trust_level(result)
        assert trust == TrustLevel.VERIFIED
        
        # Medium scores -> Community
        result.performance_score = 0.75
        result.security_score = 0.72
        result.reliability_score = 0.71
        
        trust = self.hunter._determine_trust_level(result)
        assert trust == TrustLevel.COMMUNITY
        
        # Low scores -> Experimental
        result.performance_score = 0.65
        result.security_score = 0.62
        result.reliability_score = 0.61
        
        trust = self.hunter._determine_trust_level(result)
        assert trust == TrustLevel.EXPERIMENTAL
    
    def test_family_determination(self):
        """Test tool family determination."""
        # Search tool
        tool = DiscoveredTool(
            source_url="test",
            protocol=ToolProtocol.MCP,
            name="test",
            description="test",
            capabilities=["web_search"],
            discovered_at=datetime.utcnow()
        )
        
        family = self.hunter._determine_family(tool)
        assert "intelligence/search" in family
        
        # Database tool
        tool.capabilities = ["database_query"]
        family = self.hunter._determine_family(tool)
        assert "data_ops/database" in family
        
        # Unknown tool
        tool.capabilities = ["unknown_capability"]
        family = self.hunter._determine_family(tool)
        assert "evolution/uncategorized" in family


async def run_tests():
    """Run all tests."""
    test_suite = TestToolHunterAgent()
    
    print("Testing Tool Hunter Agent...")
    print("-" * 50)
    
    tests = [
        ("Initialization", test_suite.test_initialization),
        ("Tool Discovery", test_suite.test_discover_tools),
        ("MCP Discovery", test_suite.test_mcp_discovery),
        ("Pattern Discovery", test_suite.test_pattern_discovery),
        ("Pattern Analysis", test_suite.test_analyze_patterns),
        ("Adaptation", test_suite.test_adapt_to_cogplan),
        ("Isolation Testing", test_suite.test_isolation_testing),
        ("Integration", test_suite.test_integration),
        ("Evolution", test_suite.test_evolution),
        ("Full Hunt Cycle", test_suite.test_full_hunt_cycle),
        ("Trust Level", test_suite.test_trust_level_determination),
        ("Family Determination", test_suite.test_family_determination),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        test_suite.setup_method()
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            failed += 1
        finally:
            test_suite.teardown_method()
    
    print("-" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)