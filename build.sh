#!/bin/bash

eval "$(conda shell.bash hook)"

if ! conda env list | grep -q "^cannonballgame\s"; then
    conda create -n cannonballgame python=3 -y
fi

conda activate cannonballgame

if [[ "$CONDA_DEFAULT_ENV" != "cannonballgame" ]]; then
    echo "Error: cannonballgame environment not activated"
    exit 1
fi

if [[ "$CONDA_DEFAULT_ENV" == "cannonballgame" ]]; then
    echo "Using Python from: $(which python)"
    echo "Python version: $(python --version)"

    pip install -r requirements.txt
else
    echo "Error: cannonballgame environment must be activated. Run 'conda activate cannonballgame' to activate it."
    exit 1
fi