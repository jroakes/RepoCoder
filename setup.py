# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="repocoder",
    version="0.1.9",
    author="JR Oakes",
    author_email="jroakes@gmail.com",
    description="A tool for analyzing and modifying code repositories using LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jroakes/repocoder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-generativeai",
        "python-dotenv",
        "anthropic",
    ],
)
