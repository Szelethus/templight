#!/bin/bash

# This script **installs** pyyaml, a yaml parser for python.

mkdir pyyaml
git clone https://github.com/yaml/pyyaml pyyaml
cd pyyaml
python setup.py install
