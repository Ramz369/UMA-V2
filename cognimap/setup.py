"""
CogniMap Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="cognimap",
    version="1.0.0",
    author="CogniMap Team",
    description="Living Architecture Visualization System - Self-aware codebase mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cognimap/cognimap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0",
        "rich>=10.0",  # For beautiful terminal output
        "networkx>=2.6",  # For graph operations
        "fastapi>=0.68",  # For visualization backend
        "uvicorn>=0.15",  # For running FastAPI
        "websockets>=10.0",  # For real-time updates
        "sqlalchemy>=1.4",  # For graph storage
        "aiofiles>=0.8",  # For async file operations
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.18",
            "pytest-cov>=3.0",
            "black>=22.0",
            "mypy>=0.910",
            "flake8>=4.0",
        ],
        "visualization": [
            "plotly>=5.0",  # For graph visualization
            "dash>=2.0",  # For interactive dashboards
        ],
        "ml": [
            "sentence-transformers>=2.0",  # For semantic analysis
            "scikit-learn>=1.0",  # For clustering and analysis
        ]
    },
    entry_points={
        "console_scripts": [
            "cognimap=cognimap.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cognimap": [
            "config/*.yaml",
            "protocols/*.yaml",
            "visualizer/frontend/public/*",
            "visualizer/frontend/src/**/*",
        ],
    },
)