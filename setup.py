from setuptools import setup

setup(
    version="0.1.0",
    name="uniquipy",
    description="python cli-tool to find and handle file duplicates",
    author="Steffen Richters-Finger",
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
