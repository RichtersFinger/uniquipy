from setuptools import setup
from pathlib import Path

# read contents of README
long_description = \
    (Path(__file__).parent / "README.md").read_text(encoding="utf8")

setup(
    version="1.1.0",
    name="uniquipy",
    description="python cli-tool to find and handle file duplicates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    license_files=("LICENSE",),
    url="https://pypi.org/project/uniquipy/",
    project_urls={
        "Source": "https://github.com/RichtersFinger/uniquipy"
    },
    python_requires=">=3.9, <4",
    install_requires=[
        "click>=8.1.7,<9.0.0",
    ],
    packages=[
        "uniquipy",
    ],
    entry_points={
        "console_scripts": [
            "uniquipy = uniquipy.cli:cli",
        ]
    },
)
