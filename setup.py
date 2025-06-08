from setuptools import setup, find_packages

setup(
    name="codecrate",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "docker",
        "pytest",
        "pytest-cov",
        "flake8"
    ],
    python_requires=">=3.8",
    author="Salman78687",
    author_email="your.email@example.com",
    description="A secure code execution service using Docker containers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Salman78687/CodeCrate",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 