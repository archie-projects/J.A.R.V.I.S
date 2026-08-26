#!/usr/bin/env fish
# ============================================================
# JARVIS Phase 1: additional dependencies
# Run with: fish phase1_deps.fish
# ============================================================

echo "--- Installing system audio library (portaudio, needed by sounddevice) ---"
sudo pacman -S --needed portaudio

set -gx JARVIS_HOME ~/Documents/J.A.R.V.I.S
cd $JARVIS_HOME
source .venv/bin/activate.fish

echo "--- Installing Python packages into the venv ---"
uv pip install sounddevice webrtcvad-wheels evdev

echo ""
echo "Done. If evdev import fails at runtime with a permissions error,"
echo "confirm 'groups' includes 'input' — reboot if you haven't since Phase 0."
