#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip install -r dependencies.dat

echo "Setup complete. Activate with: source .venv/bin/activate"
