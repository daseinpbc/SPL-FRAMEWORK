# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spl-framework",
    version="3.1.0",
    author="Pamela Cuce, Shreyas G",
    author_email="pamela@dasein.works, shreyas@dasein.works",
    description="Subsumption Pattern Learning: Hierarchical foundation model agent architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daseinpbc/SPL-FRAMEWORK",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.25.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "mcp": ["mcp>=0.1.0"],
        "redis": ["redis>=5.0.0"],
    },
)
