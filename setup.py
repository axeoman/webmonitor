import os

from setuptools import setup, find_packages

setup(
    name="webmonitor",
    version="1.0.0",
    description=(
        "System that monitors website availability over the network, produces metrics ",
        "about this and passes these events through an Kafka instance into an PostgreSQL ",
        "database "
    ),
    url="https://github.com/axeoman/webmonitor",
    author="Atavin Alexey",
    author_email="axeoman@gmail.com",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "psycorg2==2.8.6",
        "kafka-python==2.0.1",
        "requests==2.24.0",
        "xdg==4.0.1",
        "pyyaml==5.3.1"
    ],
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        'console_scripts': [
            'webmonitor=webmonitor:main',
        ],
    }
)
