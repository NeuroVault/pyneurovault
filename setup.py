from setuptools import setup, find_packages

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
    description="python wrapped for NeuroVault api",

    install_requires = ["numpy","pandas","nibabel"]

)
