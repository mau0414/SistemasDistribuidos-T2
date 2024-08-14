#!/bin/bash


gnome-terminal -- bash -c "python supplier.py"
gnome-terminal -- bash -c "python warehouse.py"
gnome-terminal -- bash -c "python line.py 0"