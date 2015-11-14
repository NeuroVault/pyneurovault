from setuptools import setup, find_packages

# Get requires from requirements.txt
reqs = [line.strip() for line in open('requirements.txt').readlines()]
requirements = list(filter(None, reqs))

setup(
    # Application name:
    name="pyneurovault",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Poldracklab",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=["pyneurovault"],

    # Data
    package_data = {'pyneurovault':['data/*.nii.gz']},

    # Details
    url="http://www.neurovault.org",

    license="LICENSE.txt",
    description="python wrapper for NeuroVault api",

    install_requires = requirements,
    setup_requires=['numpy','pandas']

)
