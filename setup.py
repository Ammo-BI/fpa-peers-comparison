import os

from setuptools import find_packages, setup

import src.peers_comparison as peers_comparison

NAME = "peers_comparison"
VERSION = peers_comparison.__version__
DESCRIPTION = "Get peers data from CVM and update BigQuery tables"
AUTHOR = "AMMO Varejo FP&A Team"
PYTHON_REQUIRES = ">= 3.9.0, <3.11"

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + "/requirements.txt"
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()
        install_requires = [x for x in install_requires if x and not x.startswith("#") and not x.startswith("-")]


setup(
    name=NAME,
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
    ),
    include_package_data=True,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    license="MIT",
    python_requires=PYTHON_REQUIRES,
    install_requires=install_requires,
)
