import os
from setuptools import setup, find_packages

# Read version from version.py
with open(os.path.join("flow", "version.py")) as f:
    version_info = {}
    exec(f.read(), version_info)
    version = version_info["__version__"]

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flow",
    version=version,
    author="Moshe Swed",
    author_email="mswed@beapot.com",
    description="A package for easy Shotgrid connections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mswed/flow",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["sgtk", "python-dotenv"],
)
