#!/usr/bin/env fish
# ============================================================
# JARVIS Phase 2: online/offline router dependencies
# Run with: fish phase2_deps.fish
# ============================================================

set -gx JARVIS_HOME ~/Documents/J.A.R.V.I.S
cd $JARVIS_HOME
source .venv/bin/activate.fish

echo "--- Installing Python packages ---"
uv pip install groq python-dotenv

echo ""
echo "--- Setting up your .env file for the Groq API key ---"
if test -f $JARVIS_HOME/.env
    echo "$JARVIS_HOME/.env already exists — leaving it alone."
else
    echo "GROQ_API_KEY=" > $JARVIS_HOME/.env
    echo "Created $JARVIS_HOME/.env — edit it and paste your key after the ="
end

echo ""
echo "Get a free Groq API key at https://console.groq.com/keys (free tier, no card required)."
echo "Then edit $JARVIS_HOME/.env so it reads:  GROQ_API_KEY=gsk_xxxxxxxxxxxx"
echo "This file is already covered by .gitignore — it will never be committed."
