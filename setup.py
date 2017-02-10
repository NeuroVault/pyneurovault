from setuptools import setup, find_packages

setup(name="pyneurovault",
      version="0.1.2",
      author="Poldracklab",
      author_email="vsochat@stanford.edu",
      packages=["pyneurovault"],
      package_data = {'pyneurovault':['data/*.nii.gz']},
      url="http://www.neurovault.org",
      license="LICENSE.txt",
      description="python wrapper for NeuroVault api",
      install_requires = ["pandas","nibabel","nilearn"])
