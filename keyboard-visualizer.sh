#!/bin/bash
PYTHON_PATH=$(which python3)
COLS=$(tput cols)
LINES=$(tput lines)
resize -s 8 56 &>/dev/null
sudo $PYTHON_PATH keyboard_visualizer.py
resize -s $LINES $COLS &>/dev/null
