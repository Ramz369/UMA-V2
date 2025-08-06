#!/usr/bin/env python3
"""Tests for the Codegen Agent."""
import asyncio
import json
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.codegen_agent import (
    CodegenAgent,
    GeneratedCode,
    Implementation,
    CodeLanguage,
    FrameworkType,
    generate_pricing_api_code
)


async def test_basic_generation():
    """Test basic code generation."""
    print("Testing basic code generation...")
    
    codegen = CodegenAgent()
    
    plan = {
        "task_id": "TEST-001",
        "feature": "Simple API",
        "api_design": {
            "endpoints": ["/api/v1/test"],
            "sla": {"response_time_p99": "500ms"},
            "data_model": {"id": "string", "value": "integer"}
        }
    }
    
    implementation = await codegen.generate_implementation(plan)
    
    assert implementation.task_id == "TEST-001"
    assert len(implementation.files_created) >= 3  # API, models, service
    assert implementation.total_lines > 0
    assert len(implementation.endpoints_implemented) == 1
    
    print(f"  ✅ Generated {len(implementation.files_created)} files")
    print(f"  ✅ Total lines: {implementation.total_lines}")


async def test_complex_generation():
    """Test complex API generation with caching."""
    print("\nTesting complex generation with caching...")
    
    codegen = CodegenAgent()
    
    plan = {
        "task_id": "TEST-002",
        "feature": "Real-time pricing API with SLA",
        "api_design": {
            "endpoints": [
                "/api/v1/pricing/calculate",
                "/api/v1/pricing/quote",
                "/api/v1/pricing/history"
            ],
            "sla": {
                "response_time_p99": "100ms",  # Triggers cache generation
                "availability": "99.9%"
            },
            "data_model": {
                "product_id": "string",
                "quantity": "integer",
                "customer_tier": "enum",
                "discount_codes": "array"
            }
        }
    }
    
    implementation = await codegen.generate_implementation(plan)
    
    assert len(implementation.files_created) >= 4  # Should include cache
    assert any("cache" in f.file_path for f in implementation.files_created)
    assert len(implementation.endpoints_implemented) == 3
    
    # Check FastAPI was selected
    api_file = next(f for f in implementation.files_created if "api" in f.file_path)
    assert api_file.framework == FrameworkType.FASTAPI
    assert api_file.language == CodeLanguage.PYTHON
    
    print(f"  ✅ Generated {len(implementation.files_created)} files including cache")
    print(f"  ✅ Framework: {api_file.framework.value}")


async def test_pilot_001_compatibility():
    """Test PILOT-001 compatibility."""
    print("\nTesting PILOT-001 compatibility...")
    
    plan = {
        "api_design": {
            "endpoints": [
                "/api/v1/pricing/calculate",
                "/api/v1/pricing/quote",
                "/api/v1/pricing/history"
            ],
            "sla": {
                "response_time_p99": "100ms",
                "availability": "99.9%",
                "rate_limit": "1000 req/min"
            },
            "data_model": {
                "product_id": "string",
                "quantity": "integer",
                "customer_tier": "enum",
                "discount_codes": "array"
            }
        },
        "feature": "Real-time pricing API"
    }
    
    result = await generate_pricing_api_code(plan)
    
    assert "files_created" in result
    assert "lines_of_code" in result
    assert "endpoints_implemented" in result
    assert len(result["endpoints_implemented"]) == 3
    assert result["lines_of_code"] > 100
    
    print(f"  ✅ Files created: {result['files_created'][:2]}...")
    print(f"  ✅ Lines of code: {result['lines_of_code']}")
    print(f"  ✅ Endpoints: {len(result['endpoints_implemented'])}")


async def test_language_selection():
    """Test language selection logic."""
    print("\nTesting language selection...")
    
    codegen = CodegenAgent()
    
    # Test Python selection
    python_plan = {
        "feature": "Data analytics API",
        "api_design": {"endpoints": ["/api/analyze"], "sla": {}, "data_model": {}}
    }
    impl = await codegen.generate_implementation(python_plan)
    assert impl.files_created[0].language == CodeLanguage.PYTHON
    print("  ✅ Python selected for data/analytics")
    
    # Test TypeScript selection
    ts_plan = {
        "feature": "Real-time dashboard UI",
        "api_design": {"endpoints": ["/api/stream"], "sla": {}, "data_model": {}}
    }
    impl = await codegen.generate_implementation(ts_plan)
    assert impl.files_created[0].language == CodeLanguage.TYPESCRIPT
    print("  ✅ TypeScript selected for real-time/UI")


async def test_metrics_tracking():
    """Test metrics tracking."""
    print("\nTesting metrics tracking...")
    
    codegen = CodegenAgent()
    
    # Generate multiple implementations
    for i in range(3):
        plan = {
            "task_id": f"METRIC-{i}",
            "feature": f"API {i}",
            "api_design": {
                "endpoints": [f"/api/v{i}/test"],
                "sla": {},
                "data_model": {"test": "string"}
            }
        }
        await codegen.generate_implementation(plan)
    
    metrics = codegen.get_metrics()
    
    assert metrics["agent"] == "codegen"
    assert metrics["implementations_created"] == 3
    assert metrics["total_lines_generated"] > 0
    assert metrics["avg_lines_per_implementation"] > 0
    
    print(f"  ✅ Implementations: {metrics['implementations_created']}")
    print(f"  ✅ Total lines: {metrics['total_lines_generated']}")
    print(f"  ✅ Avg lines: {metrics['avg_lines_per_implementation']:.0f}")


async def test_generated_code_quality():
    """Test that generated code has proper structure."""
    print("\nTesting generated code quality...")
    
    codegen = CodegenAgent()
    
    plan = {
        "feature": "Test API",
        "api_design": {
            "endpoints": ["/api/v1/test"],
            "sla": {"response_time_p99": "100ms"},
            "data_model": {"id": "string"}
        }
    }
    
    implementation = await codegen.generate_implementation(plan)
    
    # Check API file content
    api_file = next(f for f in implementation.files_created if "api" in f.file_path)
    assert "FastAPI" in api_file.content or "express" in api_file.content
    assert "@app" in api_file.content or "app." in api_file.content
    
    # Check models file
    model_file = next(f for f in implementation.files_created if "model" in f.file_path)
    assert "class" in model_file.content or "interface" in model_file.content
    
    # Check service file
    service_file = next(f for f in implementation.files_created if "service" in f.file_path)
    assert "async def" in service_file.content or "async function" in service_file.content
    
    print("  ✅ API file has proper structure")
    print("  ✅ Models properly defined")
    print("  ✅ Service logic implemented")


async def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Testing Codegen Agent Implementation")
    print("=" * 50)
    
    await test_basic_generation()
    await test_complex_generation()
    await test_pilot_001_compatibility()
    await test_language_selection()
    await test_metrics_tracking()
    await test_generated_code_quality()
    
    print("\n" + "=" * 50)
    print("✅ All Codegen Agent tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_all_tests())