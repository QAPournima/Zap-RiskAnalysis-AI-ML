"""
Setup configuration for ML Risk Analysis System
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "docs", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements
def read_requirements(filename):
    req_path = os.path.join(os.path.dirname(__file__), "requirements", filename)
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="ml-bug-prediction",
    version="2.0.0",
    author="Pournima Tele",
    author_email="qa-team@company.com",
    description="AI-powered JIRA bug risk analysis and prediction system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/QAPournima/RiskAnalysis-AI-ML",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # Dependencies
    install_requires=read_requirements("requirements_webapp.txt"),
    extras_require={
        "dev": ["pytest", "pytest-cov", "black", "flake8", "mypy"],
        "notebook": read_requirements("requirements.txt"),
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "ml-bug-dashboard=ml_bug_prediction.app:main",
            "ml-bug-setup=scripts.setup_environment:main",
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: proprietary commercial License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    
    # Include additional files
    include_package_data=True,
    package_data={
        "ml_bug_prediction": [
            "templates/*.html",
            "static/*",
        ],
    },
    
    # Testing
    test_suite="tests",
    tests_require=["pytest", "pytest-cov"],
) 