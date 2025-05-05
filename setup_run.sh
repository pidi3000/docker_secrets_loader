#!/bin/bash

# this script will setup the venv and run main.py

set -e  # Exit on any error
set -u  # Treat unset variables as an error

# Define the virtual environment directory
VENV_DIR=".venv"

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip and install requirements
echo "Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  echo "requirements.txt not found, skipping installation."
fi

# Run the Python script
echo "Running main.py..."
python main.py
