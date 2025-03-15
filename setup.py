#!/usr/bin/env python
"""Setup script for NBA PrizePicks Predictor."""

from setuptools import setup, find_packages

setup(
    name="nba_prizepicks",
    version="0.1.0",
    description="NBA PrizePicks Predictor with Machine Learning",
    author="Shane Janney",
    packages=find_packages(),
    install_requires=[
        "rich>=13.7.0",
        "requests>=2.31.0",
        "pandas>=2.1.3",
        "numpy>=1.26.2",
        "scikit-learn>=1.3.2",
        "matplotlib>=3.8.2",
        "nba_api>=1.3.1",
        "joblib>=1.3.2",
        "typer>=0.9.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
    ],
    extras_require={
        "scraper": [
            "requests-html>=0.10.0",
            "lxml_html_clean>=1.0.0",
        ],
        "tests": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "nba-prizepicks=nba_prizepicks.__main__:app",
        ],
    },
) 