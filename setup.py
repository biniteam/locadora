"""
Setup script para facilitar a instalação e configuração
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="locadora-strealit",
    version="4.9.0",
    description="Sistema de Locadora de Veículos",
    author="J.A. MARCELLO & CIA LTDA",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "locadora=app8:main",
        ],
    },
)
