#!/bin/bash

#!/bin/bash

# Diretório alvo
DIRECTORY="output"

# Verifica se o diretório existe
if [ -d "$DIRECTORY" ]; then
    # Remove todos os arquivos do diretório
    rm -f "$DIRECTORY"/*
    echo "Todos os arquivos foram removidos de $DIRECTORY."
else
    echo "O diretório $DIRECTORY não existe."
fi


gnome-terminal -- bash -c "python3 supplier.py"
gnome-terminal -- bash -c "python3 product_stock.py"
gnome-terminal -- bash -c "python3 warehouse.py"
gnome-terminal -- bash -c "python3 line.py 0 0"
gnome-terminal -- bash -c "python3 line.py 1 0"
gnome-terminal -- bash -c "python3 line.py 2 0"
gnome-terminal -- bash -c "python3 line.py 3 0"
gnome-terminal -- bash -c "python3 line.py 4 0"
gnome-terminal -- bash -c "python3 line.py 0 1"
gnome-terminal -- bash -c "python3 line.py 1 1"
gnome-terminal -- bash -c "python3 line.py 2 1"
gnome-terminal -- bash -c "python3 line.py 3 1"
gnome-terminal -- bash -c "python3 line.py 4 1"
gnome-terminal -- bash -c "python3 line.py 0 1"
gnome-terminal -- bash -c "python3 line.py 1 1"
gnome-terminal -- bash -c "python3 line.py 2 1"
gnome-terminal -- bash -c "python3 factory.py empurrada 0 5 48"
gnome-terminal -- bash -c "python3 factory.py puxada 1 8 48"