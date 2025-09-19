#!/bin/bash

TMUX_CONF="$HOME/.tmux.conf"
SESSION="CPCReady"
SCRIPT_TO_RUN="/home/destroyer/Projects/CPCReady2/etc/pepe.sh"  # Script que quieres ejecutar en el panel derecho inferior

# Mata la sesión si ya existe
tmux has-session -t $SESSION 2>/dev/null && tmux kill-session -t $SESSION

# Barra derecha: hora + CPU
STATUS_RIGHT='#[bold]%H:%M:%S #[fg=cyan]#(top -bn1 | grep "Cpu(s)" | awk "{printf \"%.1f%%\", $2+$4}")'

# Barra izquierda: logo CPC estilo pixel art
STATUS_LEFT='#[fg=red]█#[fg=red]█#[fg=green]█#[fg=green]█#[fg=blue]█#[fg=blue]█ #[fg=yellow]CPC'

# Panel principal con PROMPT_COMMAND para disparar script en el panel derecho inferior
tmux -f "$TMUX_CONF" new-session -s $SESSION "bash --rcfile <(echo 'PROMPT_COMMAND=\"tmux send-keys -t $SESSION:0.2 \\\"$SCRIPT_TO_RUN\\\" C-m\"; \$PROMPT_COMMAND')" \; \
    split-window -h bash \; \
    resize-pane -R 70 \; \
    split-window -v -t $SESSION:0.1 bash \; \
    select-pane -t 0 \; \
    set-option -g status-left "$STATUS_LEFT" \; \
    set-option -g status-right "$STATUS_RIGHT" \; \
    set-option -g pane-border-style "fg=white" \; \
    set-option -g pane-active-border-style "fg=white" \; \
    attach