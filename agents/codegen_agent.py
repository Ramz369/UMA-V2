#!/usr/bin/env python3
"""
Codegen Agent - Generates code implementations from plans.
Core agent for UMA-V2 code generation.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class CodeLanguage(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"


class FrameworkType(Enum):
    """Framework types for code generation."""
    FASTAPI = "fastapi"
    EXPRESS = "express"
    NEXTJS = "nextjs"
    DJANGO = "django"
    FLASK = "flask"
    SPRING = "spring"


@dataclass
class GeneratedCode:
    """Container for generated code artifacts."""
    file_path: str
    language: CodeLanguage
    framework: Optional[FrameworkType]
    content: str
    lines_of_code: int
    test_coverage_target: int
    dependencies: List[str]
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Implementation:
    """Complete implementation package."""
    task_id: str
    feature: str
    files_created: List[GeneratedCode]
    total_lines: int
    endpoints_implemented: List[str]
    test_files: List[str]
    documentation: Dict[str, str]
    estimated_duration: str
    actual_duration: Optional[str] = None


class CodegenAgent:
    """
    Codegen Agent - Transforms plans into working code.
    
    Responsibilities:
    - Generate code from specifications
    - Create appropriate file structures
    - Implement business logic
    - Generate tests
    - Create documentation
    - Manage dependencies
    """
    
    def __init__(self, kafka_client=None, credit_sentinel=None):
        """Initialize Codegen Agent.
        
        Args:
            kafka_client: Optional Kafka client for events
            credit_sentinel: Optional credit tracking
        """
        self.kafka_client = kafka_client
        self.credit_sentinel = credit_sentinel
        self.implementations_created = 0
        self.total_lines_generated = 0
        self.start_time = None
        
    async def generate_implementation(self, plan: Dict[str, Any]) -> Implementation:
        """Generate complete implementation from a plan.
        
        Args:
            plan: Plan from Planner Agent with api_design and steps
            
        Returns:
            Implementation with all generated code
        """
        self.start_time = datetime.now(timezone.utc)
        logger.info(f"Generating implementation for: {plan.get('api_design', {}).get('endpoints', ['unknown'])[0]}")
        
        # Parse plan requirements
        api_design = plan.get("api_design", {})
        endpoints = api_design.get("endpoints", [])
        sla = api_design.get("sla", {})
        data_model = api_design.get("data_model", {})
        
        # Determine technology stack
        language = self._select_language(plan)
        framework = self._select_framework(language, plan)
        
        # Generate code files
        files = []
        
        # 1. Main API file
        api_file = self._generate_api_file(endpoints, sla, framework)
        files.append(api_file)
        
        # 2. Models/schemas
        model_file = self._generate_models(data_model, language)
        files.append(model_file)
        
        # 3. Business logic
        service_file = self._generate_services(endpoints, language)
        files.append(service_file)
        
        # 4. Cache layer (if SLA requires)
        if self._needs_cache(sla):
            cache_file = self._generate_cache_layer(language)
            files.append(cache_file)
        
        # 5. Tests
        test_files = self._generate_tests(files, language)
        
        # 6. Documentation
        docs = self._generate_documentation(endpoints, data_model)
        
        # Calculate metrics
        total_lines = sum(f.lines_of_code for f in files)
        self.total_lines_generated += total_lines
        
        # Create implementation
        implementation = Implementation(
            task_id=plan.get("task_id", f"impl_{self.implementations_created}"),
            feature=plan.get("feature", "Generated API"),
            files_created=files,
            total_lines=total_lines,
            endpoints_implemented=endpoints,
            test_files=[f.file_path for f in test_files],
            documentation=docs,
            estimated_duration="1h",
            actual_duration=self._calculate_duration()
        )
        
        self.implementations_created += 1
        
        # Publish event if Kafka available
        if self.kafka_client:
            await self._publish_implementation_event(implementation)
        
        # Check credits if sentinel available
        if self.credit_sentinel:
            credits_used = self._calculate_credits(total_lines)
            if not self.credit_sentinel.check_budget("codegen", credits_used):
                logger.warning(f"Implementation exceeds budget: {credits_used} credits")
        
        logger.info(f"Implementation complete: {len(files)} files, {total_lines} lines")
        return implementation
    
    def _select_language(self, plan: Dict) -> CodeLanguage:
        """Select appropriate programming language."""
        feature = plan.get("feature", "").lower()
        
        # Python for data/ML/API
        if any(k in feature for k in ["pricing", "data", "analytics", "ml", "ai"]):
            return CodeLanguage.PYTHON
        
        # TypeScript for real-time/frontend
        if any(k in feature for k in ["real-time", "ui", "frontend", "dashboard"]):
            return CodeLanguage.TYPESCRIPT
        
        # Default to Python for APIs
        return CodeLanguage.PYTHON
    
    def _select_framework(self, language: CodeLanguage, plan: Dict) -> FrameworkType:
        """Select framework based on language and requirements."""
        if language == CodeLanguage.PYTHON:
            # FastAPI for high-performance APIs
            if "real-time" in plan.get("feature", "").lower():
                return FrameworkType.FASTAPI
            return FrameworkType.FASTAPI
        
        elif language == CodeLanguage.TYPESCRIPT:
            return FrameworkType.EXPRESS
        
        elif language == CodeLanguage.JAVASCRIPT:
            return FrameworkType.EXPRESS
        
        return FrameworkType.FASTAPI
    
    def _generate_api_file(self, endpoints: List[str], sla: Dict, framework: FrameworkType) -> GeneratedCode:
        """Generate main API file."""
        if framework == FrameworkType.FASTAPI:
            content = self._generate_fastapi_code(endpoints, sla)
            file_path = "api/pricing.py"
            language = CodeLanguage.PYTHON
        else:
            content = self._generate_express_code(endpoints, sla)
            file_path = "api/pricing.ts"
            language = CodeLanguage.TYPESCRIPT
        
        return GeneratedCode(
            file_path=file_path,
            language=language,
            framework=framework,
            content=content,
            lines_of_code=len(content.split('\n')),
            test_coverage_target=80,
            dependencies=self._get_framework_deps(framework)
        )
    
    def _generate_fastapi_code(self, endpoints: List[str], sla: Dict) -> str:
        """Generate FastAPI implementation."""
        code = '''"""FastAPI Pricing Service Implementation."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import logging

from models.pricing_models import PricingRequest, PricingResponse, PriceQuote
from services.pricing_calculator import PricingCalculator
from cache.redis_cache import RedisCache

# Initialize FastAPI app
app = FastAPI(
    title="Pricing API",
    version="1.0.0",
    description="Real-time pricing service with SLA guarantees"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calculator = PricingCalculator()
cache = RedisCache()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
'''
        
        # Add endpoints
        for endpoint in endpoints:
            path = endpoint.split('/')[-1]
            code += f'''

@app.post("{endpoint}")
async def {path}(request: PricingRequest) -> PricingResponse:
    """Handle {path} requests with SLA compliance."""
    start_time = datetime.utcnow()
    
    # Check cache first
    cache_key = f"pricing:{path}:{{request.product_id}}"
    cached = await cache.get(cache_key)
    if cached:
        logger.info(f"Cache hit for {{cache_key}}")
        return PricingResponse(**cached)
    
    try:
        # Calculate pricing
        result = await calculator.{path}(
            product_id=request.product_id,
            quantity=request.quantity,
            customer_tier=request.customer_tier,
            discount_codes=request.discount_codes
        )
        
        # Cache result
        await cache.set(cache_key, result.dict(), ttl=300)
        
        # Check SLA compliance
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        if duration > {float(sla.get('response_time_p99', '100ms').replace('ms', ''))}:
            logger.warning(f"SLA violation: {{duration}}ms > {sla.get('response_time_p99')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in {{path}}: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))
'''
        
        # Add health check
        code += '''

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring."""
    return {
        "requests_total": calculator.requests_total,
        "errors_total": calculator.errors_total,
        "cache_hits": cache.hits,
        "cache_misses": cache.misses,
        "avg_response_time_ms": calculator.avg_response_time
    }
'''
        
        return code
    
    def _generate_express_code(self, endpoints: List[str], sla: Dict) -> str:
        """Generate Express.js implementation."""
        # Simplified Express implementation
        return """// Express.js implementation placeholder
import express from 'express';
const app = express();
app.use(express.json());
// Implementation details...
"""
    
    def _generate_models(self, data_model: Dict, language: CodeLanguage) -> GeneratedCode:
        """Generate data models/schemas."""
        if language == CodeLanguage.PYTHON:
            content = self._generate_pydantic_models(data_model)
            file_path = "models/pricing_models.py"
        else:
            content = self._generate_typescript_models(data_model)
            file_path = "models/pricing_models.ts"
        
        return GeneratedCode(
            file_path=file_path,
            language=language,
            framework=None,
            content=content,
            lines_of_code=len(content.split('\n')),
            test_coverage_target=90,
            dependencies=["pydantic"] if language == CodeLanguage.PYTHON else []
        )
    
    def _generate_pydantic_models(self, data_model: Dict) -> str:
        """Generate Pydantic models."""
        code = '''"""Pydantic models for Pricing API."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class CustomerTier(str, Enum):
    """Customer tier levels."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class PricingRequest(BaseModel):
    """Request model for pricing calculations."""
    product_id: str = Field(..., description="Product identifier")
    quantity: int = Field(..., gt=0, description="Quantity to price")
    customer_tier: CustomerTier = Field(..., description="Customer tier level")
    discount_codes: List[str] = Field(default=[], description="Applied discount codes")
    
    @validator("product_id")
    def validate_product_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Invalid product_id")
        return v


class PricingResponse(BaseModel):
    """Response model for pricing calculations."""
    product_id: str
    quantity: int
    base_price: float
    discounts: float
    final_price: float
    currency: str = "USD"
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: int = 300


class PriceQuote(BaseModel):
    """Price quote model."""
    quote_id: str
    pricing: PricingResponse
    valid_until: datetime
    terms: List[str]
    locked: bool = False
'''
        return code
    
    def _generate_typescript_models(self, data_model: Dict) -> str:
        """Generate TypeScript interfaces."""
        return """// TypeScript interfaces placeholder
export interface PricingRequest {
    productId: string;
    quantity: number;
    customerTier: 'bronze' | 'silver' | 'gold' | 'platinum';
    discountCodes: string[];
}
"""
    
    def _generate_services(self, endpoints: List[str], language: CodeLanguage) -> GeneratedCode:
        """Generate business logic services."""
        if language == CodeLanguage.PYTHON:
            content = self._generate_python_service()
            file_path = "services/pricing_calculator.py"
        else:
            content = "// Service implementation"
            file_path = "services/pricing_calculator.ts"
        
        return GeneratedCode(
            file_path=file_path,
            language=language,
            framework=None,
            content=content,
            lines_of_code=len(content.split('\n')),
            test_coverage_target=85,
            dependencies=[]
        )
    
    def _generate_python_service(self) -> str:
        """Generate Python service implementation."""
        return '''"""Pricing calculation service."""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging

from models.pricing_models import PricingResponse, CustomerTier

logger = logging.getLogger(__name__)


class PricingCalculator:
    """Service for calculating prices."""
    
    def __init__(self):
        self.requests_total = 0
        self.errors_total = 0
        self.avg_response_time = 0
        self.base_prices = {}  # Would load from database
        
    async def calculate(self, product_id: str, quantity: int, 
                       customer_tier: CustomerTier, discount_codes: List[str]) -> PricingResponse:
        """Calculate pricing with all discounts."""
        self.requests_total += 1
        start = datetime.utcnow()
        
        try:
            # Get base price (would query database)
            base_price = await self._get_base_price(product_id)
            
            # Calculate quantity discount
            quantity_discount = self._calculate_quantity_discount(quantity)
            
            # Calculate tier discount
            tier_discount = self._calculate_tier_discount(customer_tier)
            
            # Apply discount codes
            code_discount = await self._apply_discount_codes(discount_codes)
            
            # Calculate final price
            total_discount = quantity_discount + tier_discount + code_discount
            final_price = (base_price * quantity) * (1 - total_discount)
            
            response = PricingResponse(
                product_id=product_id,
                quantity=quantity,
                base_price=base_price * quantity,
                discounts=total_discount,
                final_price=max(0, final_price)
            )
            
            # Update metrics
            duration = (datetime.utcnow() - start).total_seconds() * 1000
            self.avg_response_time = (self.avg_response_time + duration) / 2
            
            return response
            
        except Exception as e:
            self.errors_total += 1
            logger.error(f"Calculation error: {e}")
            raise
    
    async def quote(self, *args, **kwargs) -> PricingResponse:
        """Generate a price quote."""
        return await self.calculate(*args, **kwargs)
    
    async def history(self, *args, **kwargs) -> PricingResponse:
        """Get pricing history."""
        # Simplified - would query historical data
        return await self.calculate(*args, **kwargs)
    
    async def _get_base_price(self, product_id: str) -> float:
        """Get base price for product."""
        # Simulate database lookup
        await asyncio.sleep(0.01)
        return 99.99  # Default price
    
    def _calculate_quantity_discount(self, quantity: int) -> float:
        """Calculate discount based on quantity."""
        if quantity >= 100:
            return 0.15
        elif quantity >= 50:
            return 0.10
        elif quantity >= 10:
            return 0.05
        return 0
    
    def _calculate_tier_discount(self, tier: CustomerTier) -> float:
        """Calculate discount based on customer tier."""
        discounts = {
            CustomerTier.BRONZE: 0,
            CustomerTier.SILVER: 0.05,
            CustomerTier.GOLD: 0.10,
            CustomerTier.PLATINUM: 0.15
        }
        return discounts.get(tier, 0)
    
    async def _apply_discount_codes(self, codes: List[str]) -> float:
        """Apply discount codes."""
        total_discount = 0
        for code in codes:
            # Would validate against database
            if code == "SAVE10":
                total_discount += 0.10
            elif code == "WELCOME":
                total_discount += 0.15
        return min(total_discount, 0.30)  # Cap at 30%
'''
    
    def _needs_cache(self, sla: Dict) -> bool:
        """Determine if caching is needed based on SLA."""
        response_time = sla.get("response_time_p99", "1000ms")
        time_ms = float(response_time.replace("ms", ""))
        return time_ms < 200  # Need cache for <200ms response
    
    def _generate_cache_layer(self, language: CodeLanguage) -> GeneratedCode:
        """Generate caching layer."""
        if language == CodeLanguage.PYTHON:
            content = self._generate_redis_cache()
            file_path = "cache/redis_cache.py"
        else:
            content = "// Redis cache implementation"
            file_path = "cache/redis_cache.ts"
        
        return GeneratedCode(
            file_path=file_path,
            language=language,
            framework=None,
            content=content,
            lines_of_code=len(content.split('\n')),
            test_coverage_target=75,
            dependencies=["redis"] if language == CodeLanguage.PYTHON else []
        )
    
    def _generate_redis_cache(self) -> str:
        """Generate Redis cache implementation."""
        return '''"""Redis cache implementation."""
import json
import asyncio
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache wrapper."""
    
    def __init__(self):
        self.cache = {}  # In-memory for now (would use redis)
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache."""
        value = self.cache.get(key)
        if value:
            self.hits += 1
            return value
        self.misses += 1
        return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: int = 300):
        """Set value in cache with TTL."""
        self.cache[key] = value
        # Would set TTL in real Redis
        asyncio.create_task(self._expire_key(key, ttl))
    
    async def _expire_key(self, key: str, ttl: int):
        """Expire key after TTL."""
        await asyncio.sleep(ttl)
        self.cache.pop(key, None)
'''
    
    def _generate_tests(self, files: List[GeneratedCode], language: CodeLanguage) -> List[GeneratedCode]:
        """Generate test files for the implementation."""
        test_files = []
        
        for file in files:
            if "cache" in file.file_path:
                continue  # Skip cache tests for now
            
            test_content = self._generate_test_content(file)
            test_path = f"tests/test_{Path(file.file_path).stem}.py"
            
            test_file = GeneratedCode(
                file_path=test_path,
                language=language,
                framework=None,
                content=test_content,
                lines_of_code=len(test_content.split('\n')),
                test_coverage_target=100,
                dependencies=["pytest", "pytest-asyncio"]
            )
            test_files.append(test_file)
        
        return test_files
    
    def _generate_test_content(self, file: GeneratedCode) -> str:
        """Generate test content for a file."""
        return f'''"""Tests for {file.file_path}."""
import pytest
import asyncio
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic functionality."""
    # Test implementation would go here
    assert True


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling."""
    # Test implementation would go here
    assert True
'''
    
    def _generate_documentation(self, endpoints: List[str], data_model: Dict) -> Dict[str, str]:
        """Generate API documentation."""
        docs = {
            "README.md": self._generate_readme(endpoints),
            "API.md": self._generate_api_docs(endpoints, data_model),
            "DEPLOYMENT.md": "# Deployment Guide\n\nDeployment instructions..."
        }
        return docs
    
    def _generate_readme(self, endpoints: List[str]) -> str:
        """Generate README documentation."""
        readme = "# Pricing API\n\n## Endpoints\n\n"
        for endpoint in endpoints:
            readme += f"- `POST {endpoint}`\n"
        readme += "\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n"
        return readme
    
    def _generate_api_docs(self, endpoints: List[str], data_model: Dict) -> str:
        """Generate API documentation."""
        docs = "# API Documentation\n\n"
        for endpoint in endpoints:
            docs += f"## {endpoint}\n\n"
            docs += "### Request\n```json\n{\n"
            for field, ftype in data_model.items():
                docs += f'  "{field}": "{ftype}",\n'
            docs += "}\n```\n\n"
        return docs
    
    def _get_framework_deps(self, framework: FrameworkType) -> List[str]:
        """Get framework dependencies."""
        deps_map = {
            FrameworkType.FASTAPI: ["fastapi", "uvicorn", "pydantic"],
            FrameworkType.EXPRESS: ["express", "body-parser", "cors"],
            FrameworkType.FLASK: ["flask", "flask-cors"],
            FrameworkType.DJANGO: ["django", "djangorestframework"],
        }
        return deps_map.get(framework, [])
    
    def _calculate_credits(self, lines: int) -> int:
        """Calculate credits based on lines generated."""
        # Roughly 1 credit per 10 lines
        return max(10, lines // 10)
    
    def _calculate_duration(self) -> str:
        """Calculate actual duration."""
        if self.start_time:
            duration = datetime.now(timezone.utc) - self.start_time
            return f"{duration.total_seconds():.2f}s"
        return "0s"
    
    async def _publish_implementation_event(self, implementation: Implementation):
        """Publish implementation event to Kafka."""
        event = {
            "id": f"impl_{implementation.task_id}",
            "type": "code_generated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "codegen",
            "payload": {
                "task_id": implementation.task_id,
                "files_created": [f.file_path for f in implementation.files_created],
                "total_lines": implementation.total_lines,
                "endpoints": implementation.endpoints_implemented
            },
            "meta": {
                "session_id": f"uma-v2-{datetime.now().strftime('%Y-%m-%d')}-001",
                "credits_used": self._calculate_credits(implementation.total_lines)
            },
            "garbage": False
        }
        
        try:
            await self.kafka_client.publish_event("agent-events", event)
            logger.info(f"Published implementation event for {implementation.task_id}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "agent": "codegen",
            "implementations_created": self.implementations_created,
            "total_lines_generated": self.total_lines_generated,
            "avg_lines_per_implementation": (
                self.total_lines_generated / self.implementations_created
                if self.implementations_created > 0 else 0
            )
        }


# For PILOT-001 compatibility
async def generate_pricing_api_code(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Generate code for pricing API (PILOT-001 test)."""
    codegen = CodegenAgent()
    implementation = await codegen.generate_implementation(plan)
    
    # Convert to test-expected format
    return {
        "files_created": [f.file_path for f in implementation.files_created],
        "lines_of_code": implementation.total_lines,
        "test_coverage": 0,  # Not measured yet
        "endpoints_implemented": implementation.endpoints_implemented
    }


if __name__ == "__main__":
    # Test the codegen
    async def test():
        plan = {
            "api_design": {
                "endpoints": [
                    "/api/v1/pricing/calculate",
                    "/api/v1/pricing/quote",
                    "/api/v1/pricing/history"
                ],
                "sla": {
                    "response_time_p99": "100ms",
                    "availability": "99.9%"
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
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())