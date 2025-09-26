#!/bin/bash

RED='\e[31m'
BLUE='\e[34m'
GREEN='\e[32m'
YELLOW='\e[33m'
YELLOW_BOLD='\e[1;33m'
RESET='\e[0m'


# Función para imprimir texto en color rojo.
# Uso: __cpcready_echo_red "Este es un mensaje de error"
function __cpcready_echo_red() {
  local text="$1"
  echo -e "\033[0;31m${text}\033[0m"
}

# Función para mostrar texto en color amarillo
# Uso: __cpcready_echo_yellow "Este es un mensaje de advertencia"
function __cpcready_echo_yellow() {
  local text="$1"
  echo -e "\033[0;33m${text}\033[0m"
}

# Función para mostrar texto en color azul
# Uso: __cpcready_echo_blue "Este es un mensaje informativo"
function __cpcready_echo_blue() {
  local text="$1"
  echo -e "\033[0;34m${text}\033[0m"
}

# Función para mostrar texto en color verde
# Uso: __cpcready_echo_green "Este es un mensaje de éxito"
function __cpcready_echo_green() {
  local text="$1"
  echo -e "\033[0;32m${text}\033[0m"
}

# Función para mostrar texto en color azul
# Uso: __cpcready_echo_blue "Este es un mensaje informativo"
function __cpcready_echo_command_help() {
  local text="$1"
  local description="$2"
  echo -e "\033[0;34m${text}\033[0m${description}"
}

# Función para mostrar un mensaje de error y salir del script.
# Uso: __error_exit "Mensaje de error"
function __error_exit() {
  echo "Error: $1" >&2
  exit 1
}

# Función para verificar si un archivo o directorio existe.
# Uso: if file_exists "mi_archivo.txt"; then ...
function __file_exists() {
  local path="$1"
  if [[ -e "$path" ]]; then
    return 0  # Verdadero (existe)
  else
    return 1  # Falso (no existe)
  fi
}

# funcion que devuelve la version del software
# Uso: __get_version
function __get_version(){
  version=$(cat $CPCREADY_DIR/var/VERSION)
  echo "CPCReady: $version"
}

# Función para cargar la configuración desde .cpcready.yml
# y exportarla como variables de entorno.
# Uso: __load_config
function __load_config() {
  local config_file="$CPCREADY_DIR/.cpcready.yml"
  if [[ ! -f "$config_file" ]]; then
    __cpcready_echo_red "Error: Fichero de configuración no encontrado en '$config_file'"
    return 1
  fi
  eval $(yq '. as $item | keys | .[] | "export \(. )=\"\($item[.]\)\""' "$config_file")
}

# Function to check if CPCREADY_PROJECT_CONFIG is set
# Usage: __cpcready_check_project_config_is_set
__cpcready_check_project_config_is_set() {
  if [ -z "$CPCREADY_PROJECT_CONFIG" ]; then
    __cpcready_echo_red "Error: Project configuration CPCReady project not set."
    __cpcready_echo_red "Please run 'cpc init' to create a new project."
    return 1
  fi
}