#!/usr/bin/env fish
# ============================================================
# JARVIS Project — Phase 0: Verification
# Run after phase0_setup.fish, with:  fish phase0_verify.fish
# ============================================================

set -g pass_count 0
set -g fail_count 0

function check
    set -l label $argv[1]
    set -l cmd $argv[2]
    if eval $cmd >/dev/null 2>&1
        echo "  [OK]   $label"
        set -g pass_count (math $pass_count + 1)
    else
        echo "  [FAIL] $label"
        set -g fail_count (math $fail_count + 1)
    end
end

echo "=== JARVIS Phase 0 Verification ==="
echo ""

check "NVIDIA driver (nvidia-smi)"          "nvidia-smi"
check "ydotool installed"                    "type -q ydotool"
check "grim installed"                       "type -q grim"
check "slurp installed"                      "type -q slurp"
check "tesseract installed"                  "type -q tesseract"
check "ollama installed"                     "type -q ollama"
check "ollama starter model present"         "ollama list | grep -q qwen2.5"
check "uv installed"                         "type -q uv"
set -gx JARVIS_HOME ~/Documents/J.A.R.V.I.S
check "J.A.R.V.I.S venv exists"              "test -d $JARVIS_HOME/.venv"
check "faster-whisper installed in venv"     "test -f $JARVIS_HOME/.venv/lib/python*/site-packages/faster_whisper/__init__.py"
check "piper voice .onnx present"            "test -f $JARVIS_HOME/voices/en_GB-alan-medium.onnx"
check "piper voice .json present"            "test -f $JARVIS_HOME/voices/en_GB-alan-medium.onnx.json"
check "input group membership (may need re-login)" "groups | grep -q input"

echo ""
echo "=== $pass_count passed, $fail_count failed ==="
if test $fail_count -gt 0
    echo "Fix the FAIL items above (or tell me what they say) before we move to Phase 1."
else
    echo "Environment is ready. Next: Phase 1 — the core voice loop."
end
