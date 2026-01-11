#!/bin/bash

echo "The installation has started."
python -m venv .venv
echo "[1] Virtual environment has been initialized."
source .venv/bin/activate
echo "[2] Virtual environment has been activated."
pip install -r dependencies.dat
echo "[3] Installation of dependencies has been completed"

echo "Setup complete. Activate with: source .venv/bin/activate"
