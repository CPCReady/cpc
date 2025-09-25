#!/bin/bash

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"

IDSK="$CPCREADY_DIR/opt/iDSK"

eval $(yq '. as $item | keys | .[] | "export \(.)=\($item[.])"' .cpcready.yml)

# Verifica el primer parámetro
if [ -z "$1" ]; then
  echo
  echo "Disc Ready"
  # echo "Usage: cpc disc [A/a|B/b|create] [diskfile.dsk]"
  echo 
  exit 0
else
  echo  "estás en disc con parámetro $1"
fi

ACTION=$(echo "$1" | tr '[:lower:]' '[:upper:]')

case "$ACTION" in
  A|B)
    UNIT=$ACTION
    # Verifica el segundo parámetro
    if [ -z "$2" ]; then
      # Si no hay segundo parámetro, mira las variables de entorno
      VAR_NAME="CPCREADY_DISC_$UNIT"
      DISC_PATH="${!VAR_NAME}"

      if [ -z "$DISC_PATH" ]; then
        echo
        __cpcready_echo_red "Drive $UNIT: disc missing"
        echo
        exit 1
      else
        echo "El disco asignado a la unidad $UNIT es: $DISC_PATH"
      fi
    else
      # Si hay segundo parámetro, úsalo
      if [ ! -f "$2" ]; then
        __cpcready_echo_red "El fichero '$2' no existe."
        exit 1
      fi

      if [[ ! "$2" == *.dsk ]]; then
        __cpcready_echo_red "El fichero '$2' no tiene la extensión .dsk."
        exit 1
      fi
      
      DISC_PATH=$(realpath "$2")
      echo "Se usará el disco '$DISC_PATH' para la unidad $UNIT."
      
      VAR_NAME_LOWER="drive_$(echo "$UNIT" | tr '[:upper:]' '[:lower:]')"
      sed -i "s|^$VAR_NAME_LOWER:.*|$VAR_NAME_LOWER: $DISC_PATH|" "$CPCREADY_DIR/.cpcready.yml"
    fi
    ;;
  CREATE)
    if [ -z "$2" ]; then
      __cpcready_echo_red "Para crear un disco se necesita un nombre de fichero."
      exit 1
    fi
    ;;
  *)
    __cpcready_echo_red "Parámetro no válido: $1. Use A/a, B/b o CREATE."
    exit 1
    ;;
esac