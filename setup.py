#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工离职流程日志模拟器 v1.0.0 - 安装脚本
"""

from setuptools import setup, find_packages
from version import __version__, __author__, __email__, __description__, __license__

# 读取长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取依赖包
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ub-generator",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/ub-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
        "performance": [
            "pytz>=2021.1",
            "ujson>=4.0.0",
            "psutil>=5.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ub-generator=main:main",
            "ub-verify=verify_relationships:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="employee resignation log simulator security audit compliance",
    project_urls={
        "Bug Reports": "https://github.com/your-org/ub-generator/issues",
        "Source": "https://github.com/your-org/ub-generator",
        "Documentation": "https://github.com/your-org/ub-generator/blob/main/README.md",
        "Changelog": "https://github.com/your-org/ub-generator/blob/main/CHANGELOG.md",
    },
) 