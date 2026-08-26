#!/usr/bin/env fish
set -gx JARVIS_HOME ~/Documents/J.A.R.V.I.S
cd $JARVIS_HOME
source .venv/bin/activate.fish
python -m jarvis.main
