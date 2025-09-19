#!/bin/bash
# Script para lanzar tmux con layout: dos paneles verticales, el derecho partido en dos horizontales
# El derecho es el más estrecho
SESSION="CPCReady"
CONFIG_FILE="/home/destroyer/Projects/CPCReady2/etc/terminal.conf"
TMUX="tmux -2 -f $CONFIG_FILE"

# Comprueba si la sesión ya existe
$TMUX has-session -t "$SESSION" 2>/dev/null

if [ $? != 0 ]; then
  # Arranca nueva sesión en segundo plano
  $TMUX new-session -d -s "$SESSION"
  sleep 0.2

  # Divide en vertical: izquierda (0) y derecha (1, más estrecho)
  $TMUX split-window -h -p 25 -t "$SESSION":0.0
  sleep 0.1

  # Selecciona el panel derecho (1) y lo divide en horizontal
  $TMUX select-pane -t "$SESSION":0.1
  $TMUX split-window -v -t "$SESSION":0.1
  sleep 0.1

  # Selecciona el panel izquierdo (0) al final
  $TMUX select-pane -t "$SESSION":0.0
fi

# Adjunta a la sesión
$TMUX attach-session -t "$SESSION"