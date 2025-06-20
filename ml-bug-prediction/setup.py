#!/usr/bin/env python3
"""
Setup script for ML Risk Analysis Dashboard
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

requirements = read_requirements("requirements/requirements.txt")
webapp_requirements = read_requirements("requirements/requirements_webapp.txt")

setup(
    name="ml-risk-prediction",
    version="2.0.0",
    author="Zap⚡️ Team",
    author_email="zapaitool@gmail.com",
    maintainer="Pournima Tele",
    maintainer_email="qapournima@gmail.com",
    description="AI-powered JIRA risk analysis and prediction system by Zap⚡️",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QAPournima/RiskAnalysis-AI-ML",
    project_urls={
        "Bug Tracker": "https://github.com/QAPournima/RiskAnalysis-AI-ML/issues",
        "Documentation": "https://github.com/QAPournima/RiskAnalysis-AI-ML/wiki",
        "Source Code": "https://github.com/QAPournima/RiskAnalysis-AI-ML",
        "Company": "https://zap-ai-tools.com",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Bug Tracking",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="jira, risk-analysis, machine-learning, ai, dashboard, quality-assurance, zap",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "webapp": webapp_requirements,
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    include_package_data=True,
    package_data={
        "ml_bug_prediction": ["../templates/*", "../static/*"],
    },
    entry_points={
        "console_scripts": [
            "ml-risk-analysis=ml_bug_prediction.app:main",
        ],
    },
    zip_safe=False,
    license="Proprietary Commercial License",
) 