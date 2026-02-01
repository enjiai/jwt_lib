"""Setup configuration for enjilib-jwt-auth package."""
from setuptools import setup, find_packages

setup(
    name="enjilib-jwt-auth",
    version="0.1.0",
    description="JWT authentication utilities for Enji microservices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Enji Team",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pyjwt>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
)
