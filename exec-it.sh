#!/bin/bash


gnome-terminal -- bash -c "python supplier.py"
gnome-terminal -- bash -c "python product_stock.py"
gnome-terminal -- bash -c "python warehouse.py"
gnome-terminal -- bash -c "python line.py 0"
gnome-terminal -- bash -c "python factory.py empurrada 5 48"