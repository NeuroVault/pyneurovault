from setuptools import setup, find_packages

setup(name="pyneurovault",
      version="0.1.3",
      author="Poldracklab",
      author_email="vsoch@users.noreply.github.com",
      packages=["pyneurovault"],
      package_data = {'pyneurovault':['data/*.nii.gz']},
      url="https://neurovault.org",
      license="LICENSE.txt",
      description="python wrapper for NeuroVault api",
      install_requires = ["pandas","nibabel","nilearn"])
