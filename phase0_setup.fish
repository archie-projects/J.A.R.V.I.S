#!/usr/bin/env fish
# ============================================================
# JARVIS Project — Phase 0: Environment Setup
# CachyOS / Hyprland (Caelestia) / fish shell
# ============================================================
# READ THIS FIRST:
#   - Run this on YOUR machine, not in a chat sandbox.
#   - It uses sudo for system packages — review before running.
#   - Safe to re-run; most steps are idempotent (skip if already done).
#   - Run with:  fish phase0_setup.fish

echo "=== JARVIS Phase 0: Environment Setup ==="
echo ""

# --- 1. NVIDIA / CUDA check -------------------------------------
echo "--- [1/6] Checking NVIDIA driver ---"
if not type -q nvidia-smi
    echo "nvidia-smi not found. Install a driver first, e.g.:"
    echo "  sudo pacman -S nvidia-open-dkms nvidia-utils nvidia-settings"
    echo "(check what CachyOS already installed with: pacman -Qs nvidia)"
    echo "Re-run this script after that's sorted."
    exit 1
else
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
end
echo ""

# --- 2. Core system packages -------------------------------------
echo "--- [2/6] Installing core system packages (pacman) ---"
sudo pacman -Syu --needed \
    base-devel git python python-pip \
    ydotool grim slurp wl-clipboard \
    tesseract tesseract-data-eng \
    jq curl
echo ""

# --- 3. ydotool setup (mouse/keyboard automation, needed in Phase 6) --
echo "--- [3/6] Setting up ydotool ---"
sudo usermod -aG input $USER
systemctl --user enable --now ydotool 2>/dev/null
or echo "  (ydotool user service unit not found yet — fine, we wire this properly in Phase 6)"
echo "  NOTE: log out/in once for the 'input' group membership to take effect."
echo ""

# --- 4. Ollama (offline LLM runtime) ------------------------------
echo "--- [4/6] Installing Ollama ---"
if not type -q ollama
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "  Ollama already installed."
end

echo "  Pulling starter offline model: qwen2.5:7b-instruct (Q4 quant, ~4.5GB, fits your 8GB VRAM)"
ollama pull qwen2.5:7b-instruct-q4_K_M
echo ""

# --- 5. Python project environment via uv -------------------------
echo "--- [5/6] Setting up Python project environment (uv) ---"
if not type -q uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "  uv installed — you may need to restart your shell for PATH to update."
end

set -gx JARVIS_HOME ~/Documents/J.A.R.V.I.S
mkdir -p $JARVIS_HOME
cd $JARVIS_HOME
uv venv
uv pip install faster-whisper openwakeword ollama piper-tts
echo ""

# --- 6. Starter Piper voice (en_GB, formal) -----------------------
echo "--- [6/6] Fetching a starter Piper voice (en_GB-alan, formal male) ---"
mkdir -p $JARVIS_HOME/voices
curl -L -o $JARVIS_HOME/voices/en_GB-alan-medium.onnx \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx"
curl -L -o $JARVIS_HOME/voices/en_GB-alan-medium.onnx.json \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
echo ""

echo "=== Phase 0 setup finished ==="
echo "Next: run phase0_verify.fish to confirm everything works."
