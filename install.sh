#!/bin/bash

# Ruta al archivo .bashrc
BASHRC_FILE="$HOME/.bashrc"

# Marcador único para verificar si el script ya ha sido añadido
CPCREADY_MARKER='export CPCREADY_DIR="$HOME/.cpcready"' 

if [ -d "$HOME/.cpcready" ]; then
    echo "¡CPCReady ya esta instalado en $HOME/.cpcready!"
    exit 0
else
    echo Descargando e instalando CPCReady...
fi

# Contenido a añadir
CONTENT_TO_ADD='''
# ****************************************************************
# THIS MUST BE AT THE END OF THE FILE FOR CPCREADY TO WORK!!!
# ****************************************************************

export CPCREADY_DIR="$HOME/.cpcready"
[[ -s "$HOME/.cpcready/bin/cpcready-init.sh" ]] && source "$HOME/.cpcready/bin/cpcready-init.sh"

cd() {
    # Llamar al cd original
    builtin cd "$@" || return

    # Aquí pones la lógica que quieras
    if [[ -f ".cpcready.yml" ]]; then
        export CPCREADY_PROJECT_CONFIG="$(pwd)/.cpcready.yml"
        source "$CPCREADY_DIR/etc/logo.sh"
        source "$CPCREADY_DIR/etc/env.sh"
        echo
        gum spin --spinner dot --title "CPCReady project loaded..." -- sleep 1
        # __cpcready_echo_green "CPCReady project loaded..."
        echo
    fi
}

if [[ -f "$(pwd)/.cpcready.yml" ]]; then
    source "$CPCREADY_DIR/etc/logo.sh"
    export CPCREADY_PROJECT_CONFIG="$(pwd)/.cpcready.yml"
    source "$CPCREADY_DIR/etc/env.sh"
    echo
    gum spin --spinner dot --title "CPCReady project loaded..." -- sleep 1
    echo
fi

# ****************************************************************
'''

# Verificar si el marcador ya existe en .bashrc
if grep -Fxq "$CPCREADY_MARKER" "$BASHRC_FILE"; then
    echo "La configuración de CPCReady ya existe en $BASHRC_FILE. No se requiere ninguna acción."
else
    # Añadir el contenido al final de .bashrc
    echo "Añadiendo la configuración de CPCReady a $BASHRC_FILE..."
    echo "$CONTENT_TO_ADD" >> "$BASHRC_FILE"
    echo "¡Configuración añadida con éxito!"
    echo "Por favor, reinicia tu terminal o ejecuta 'source $BASHRC_FILE' para aplicar los cambios."
fi

