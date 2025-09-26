#!/bin/bash

# Ruta al archivo .bashrc
BASHRC_FILE="$HOME/.bashrc"

# Marcador único para verificar si el script ya ha sido añadido
CPCREADY_MARKER='export CPCREADY_DIR="$HOME/.cpcready"' 

if [ -d "$HOME/.cpcready" ]; then
    echo "¡CPCReady ya esta instalado en $HOME/.cpcready!"
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
    else
        unset CPCREADY_PROJECT_CONFIG
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

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
sudo apt update && sudo apt install gum

echo "Instalando yq (YAML processor)..."
if [[ "$(uname -s)" == "Linux" && "$(uname -m)" == "x86_64" ]]; then
    YQ_URL="https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64"
    YQ_DEST="$HOME/.cpcready/opt/yq"

    mkdir -p "$HOME/.cpcready/opt"
    if curl -L "$YQ_URL" -o "$YQ_DEST" && chmod +x "$YQ_DEST"; then
        echo "yq instalado correctamente en $YQ_DEST"
    else
        echo "Error al instalar yq." >&2
    fi
else
    echo "yq no se instalará. Sistema operativo o arquitectura no soportada (se requiere Linux x86_64)."
fi

