#!/bin/bash
PYTHON_PATH=$(which python3)
PREV_COLS=$(tput cols)
PREV_LINES=$(tput lines)
resize -s 8 56 &>/dev/null
sudo $PYTHON_PATH keyboard_visualizer.py
resize -s $PREV_LINES $PREV_COLS &>/dev/null
