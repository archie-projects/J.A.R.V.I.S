# Project "JARVIS" — Local AI Desktop Assistant for CachyOS / Caelestia (Hyprland)

**Owner's environment:** CachyOS (Arch-based), Hyprland via Caelestia dotfiles (Quickshell/QML), fish shell.
**Project directory:** `~/Documents/J.A.R.V.I.S`
**Hardware:** NVIDIA RTX 5050 (8GB VRAM), 16GB RAM, Intel Core Ultra 210H.
**Constraint:** Entire stack must be buildable with $0 mandatory spend. Optional paid API keys can be plugged in later, but nothing should *require* payment to function.
**Screen-control policy:** Read + safe automation — JARVIS may open apps, type, and click, but every action that touches the mouse/keyboard/filesystem/shell requires an explicit per-action confirmation (voice or UI) until the user later decides to loosen this.

This document is meant to be handed to any AI coding agent (or read by a human) as the single source of truth for what we're building and in what order. Nothing here is final — treat versions/model names as "best known choice as of planning time," verify before installing.

---

## 1. Architecture Overview

```
 ┌────────────────────────────────────────────────────────────────┐
 │                        FRONTEND (UI App)                        │
 │  Tauri (Rust shell) + Svelte/React + Canvas/WebGL visualizer     │
 │  - Spherical reactive audio visualizer                           │
 │  - Text input box + chat log                                     │
 │  - Mode indicator (listening/thinking/speaking, online/offline)  │
 │  - Confirmation dialogs for actions                               │
 │  - Settings panel (API keys, wake word, voice, permissions)      │
 └───────────────▲───────────────────────────────┬──────────────────┘
                 │ WebSocket / IPC                │ audio stream
 ┌───────────────┴───────────────────────────────▼──────────────────┐
 │                        BACKEND (Core Daemon)                     │
 │  Python (fastest path to ML ecosystem) or Rust (perf) — see §3   │
 │                                                                    │
 │  ┌───────────┐ ┌───────────┐ ┌────────────┐ ┌──────────────┐    │
 │  │ Wake Word │→│   STT     │→│   Intent /  │→│  LLM Router  │    │
 │  │(openWake- │ │(faster-   │ │  Orchestr.  │ │(online/local)│    │
 │  │ Word)     │ │ whisper)  │ │             │ │              │    │
 │  └───────────┘ └───────────┘ └─────┬──────┘ └──────┬───────┘    │
 │                                     │                │            │
 │                     ┌───────────────▼────────────────▼───────┐   │
 │                     │           Tool / Action Layer           │   │
 │                     │ web search · file ops · code exec ·     │   │
 │                     │ screen capture/vision · mouse/keyboard · │   │
 │                     │ window mgmt (hyprctl) · app launch       │   │
 │                     └───────────────┬───────────────────────┘   │
 │                                     │                            │
 │                          ┌──────────▼─────────┐                 │
 │                          │   Safety / Sandbox  │                 │
 │                          │  allow/deny lists,  │                 │
 │                          │  confirmation gate,  │                 │
 │                          │  audit log           │                 │
 │                          └──────────┬─────────┘                 │
 │                                     │                            │
 │                              ┌──────▼──────┐                    │
 │                              │     TTS     │                    │
 │                              │   (Piper)   │                    │
 │                              └─────────────┘                    │
 └────────────────────────────────────────────────────────────────┘
```

Everything below the frontend runs as **one local backend service** (a daemon your user starts once, e.g. via a fish function or systemd user service). The Tauri UI and the future Quickshell overlay widget are both just *clients* of this daemon over a local WebSocket — this is why "core app + optional overlay widget" works cleanly.

---

## 2. Persona & Voice Identity

**Goal:** an assistant that *feels* like the Iron Man JARVIS — calm, dry-witted, formally addresses you as "sir," speaks in a polished voice — without literally reproducing the movie character's voice.

**Important boundary:** Paul Bettany's JARVIS voice is a copyrighted performance. Cloning it (even from movie clips) isn't something I'll help build, and using it would put the whole project at legal risk if you ever shared it. The good news is the *personality and accent style* are not owned by anyone — a refined, dry, formal British-assistant character is a well-worn archetype we can build freely and make genuinely yours rather than a copy.

Two layers make up the persona:

1. **Voice (TTS):** Use a high-quality open-source British-English voice as the base:
   - **Piper TTS** — has decent free `en_GB` voices (e.g. `alan`, `northern_english_male`), lightweight, fast, good enough for Phase 1-3 prototyping.
   - **Upgrade path:** **Coqui XTTS-v2** (open-source, runs locally, much more natural/expressive prosody than Piper, fits on your 8GB VRAM) once the core loop works — gives a noticeably more "premium assistant" sound. You can pick or fine-tune a formal, calm, male or female RP-British voice from consenting/open voice datasets — never from copyrighted film audio.
   - Optionally offer 2-3 selectable voices in Settings so it's "yours," not a copy of anyone specific.
2. **Character (system prompt / LLM behavior):** A persistent system prompt for the LLM router (both online and offline models) that defines: addresses the user as "sir" by default (configurable, in case you want it toggled off later), dry understated wit, concise and calm under pressure, proactively flags risks before acting (very on-brand for the confirm-before-action safety design in Phase 6-7), no filler/sycophancy. This is cheap to build — it's prompt engineering, not a new component — but it's worth its own checklist item so it doesn't get lost among the technical phases.

---

## 3. Component Choices (all free/open-source by default)

| Component | Default (offline, free) | Online alternative | Notes |
|---|---|---|---|
| Wake word | **openWakeWord** | — | Fully open-source, runs on CPU, trainable custom wake word ("Jarvis" or custom name) |
| Speech-to-text | **faster-whisper** (CUDA, `small`/`medium` model) | — | GPU-accelerated on your RTX 5050; near-instant transcription |
| LLM (offline) | **Ollama** running Llama 3.1 8B / Qwen2.5 7B / Phi-4-mini (Q4 quant) | — | ~5GB VRAM, leaves headroom for STT/vision |
| LLM (online) | User's own key OR free-tier providers | Groq (very low latency, free tier), OpenRouter free models, Google Gemini free tier, Anthropic/OpenAI if user supplies a paid key | Router picks based on mode + what keys are configured |
| Text-to-speech | **Piper TTS** (prototype) → **Coqui XTTS-v2** (polish) | — | British `en_GB` voice, formal/calm tone; see §2 for the persona/voice plan and the IP boundary around not cloning film audio |
| Vision (screen understanding) | **Moondream2** (small local VLM) or OCR via **Tesseract** | Claude/GPT-4V if online + key present | Local vision model fits comfortably in 8GB VRAM alongside quantized LLM if not run concurrently |
| Web search | **SearXNG** (self-hosted meta-search, free) | Brave Search API (free tier) | Self-hosted keeps it 100% free with no key |
| Screenshot capture | **grim** (+ `slurp` for region select) | — | Standard Wayland/Hyprland tool |
| Mouse/keyboard automation | **ydotool** | — | Works under Wayland/Hyprland (unlike xdotool) |
| Window management | **hyprctl** (Hyprland's native IPC/CLI) | — | Move/resize/focus windows, launch apps in workspaces |
| Sandboxing | **bubblewrap (bwrap)** or **firejail** | — | Wraps risky file/shell actions |
| App shell | **Tauri** (Rust + system webview) | — | Much lighter than Electron, important since GPU/RAM budget is shared with local models |
| Overlay widget (phase 8) | **Quickshell (QML)** | — | Matches Caelestia's own stack, so it can live natively in your rice |

---

## 4. Backend Language Decision (needs your input later, default assumed below)

Default assumption for this roadmap: **Python** for the backend daemon, because nearly every component above (faster-whisper, openWakeWord, Ollama client, Moondream2, Piper bindings) has first-class Python support, and prototyping speed matters more than raw performance here — the actual heavy lifting (STT/LLM/TTS inference) happens in optimized C++/CUDA under the hood regardless of what glues it together. Rust is the alternative if we want to fold the daemon into the Tauri process directly, but it will slow down early phases considerably. We'll confirm this before Phase 1 starts.

---

## 5. Phased Roadmap

### Phase 0 — Environment Prep
- Install CUDA/NVIDIA drivers + `nvidia-utils` on CachyOS, verify with `nvidia-smi`.
- Install Python 3.12 + `uv` or `pipx` for isolated envs (fish-shell-friendly).
- Install Ollama, pull one 7-8B quantized model, sanity-test generation speed.
- Install Piper TTS + one voice model, test synthesis.
- Install `ydotool` + `ydotoold` service, grant required permissions (input group), test a scripted click/type under Hyprland.
- Install `grim`, `slurp`, `hyprctl` (already present with Hyprland).
- Confirm fish shell functions/aliases we'll want (e.g. a `jarvis` launcher function).
- **Deliverable:** a checklist/script confirming every dependency is installed and working standalone, before any integration code is written.

### Phase 1 — Core Voice Loop (CLI only, no UI)
- Wire: openWakeWord → faster-whisper → (dummy echo, no LLM yet) → Piper.
- Measure end-to-end latency wake-word → spoken reply. This number determines whether later phases need optimization (streaming, smaller models, etc.).
- **Deliverable:** you say "Jarvis," speak a sentence, it's transcribed and read back to you, all in the terminal.

### Phase 2 — LLM Brain + Online/Offline Router
- Add Ollama-backed offline responses.
- Add a config system for API keys (encrypted local storage, e.g. via `keyring` or a simple encrypted file — never plaintext).
- Add at least one free-tier online provider (Groq recommended for speed).
- Build the router: explicit voice commands ("Jarvis, go offline" / "Jarvis, go online") plus automatic connectivity detection (periodic lightweight ping/DNS check) that force-switches to offline if internet drops mid-session.
- Write and wire in the **persona system prompt** (§2) — applied consistently to both the online and offline model so the "sir," dry-wit, calm-under-pressure character doesn't disappear when the mode switches.
- **Deliverable:** same CLI loop, now answering real questions in-character, switchable between local and cloud brains by voice.

### Phase 3 — The Interface
- Scaffold Tauri + Svelte (or React) app.
- Build the spherical audio visualizer: Web Audio API `AnalyserNode` reading mic input (and/or TTS output) amplitude/frequency data, driving a WebGL or Canvas sphere whose surface lines grow/shrink with volume/frequency bands. Distinct visual states for idle / listening / thinking / speaking / offline-mode / online-mode.
- Add text input box + scrollable chat history, wired to the same backend the voice loop uses (text bypasses wake-word/STT, goes straight to the LLM router).
- Add a settings panel: API key entry, wake-word sensitivity, voice selection, online/offline default, permission levels.
- **Deliverable:** a real desktop app window replacing the CLI, voice and text both working through the visualizer UI.

### Phase 4 — Tools: Search, Files, Code
- Web search tool via self-hosted SearXNG (or Brave free tier), summarized results fed back to the LLM.
- File creation/editing tool (write to disk, with path shown to user before writing).
- Code writing + execution tool: LLM writes code to a scratch dir, execution happens through the safety/sandbox layer (Phase 7 dependency — stub it here, harden later).
- Open links / launch apps via `xdg-open` and `hyprctl dispatch exec`.
- **Deliverable:** "Jarvis, search for X," "Jarvis, write a Python script that does X and run it," "Jarvis, open my browser," all working with confirmation prompts for anything that writes/executes.

### Phase 5 — Screen Awareness (read-only)
- Screenshot capture on command ("Jarvis, what's on my screen") via `grim`.
- Local vision Q&A via Moondream2 for offline mode; route to a cloud vision model if online + key configured for higher accuracy.
- OCR fallback via Tesseract for pure text-extraction cases (cheaper/faster than a full VLM call).
- **Deliverable:** JARVIS can describe/answer questions about what's currently on your screen, no actions yet.

### Phase 6 — Screen Control (confirmed automation)
- Mouse/keyboard actions via `ydotool`, window moves/focus via `hyprctl`.
- Every action is proposed first ("I'm about to click X / type Y / move window Z — proceed?") via UI dialog and/or spoken confirmation, per your chosen safety level.
- Action queue: multi-step tasks show the full plan before execution starts, with the ability to approve all, approve step-by-step, or cancel.
- **Deliverable:** "Jarvis, open Firefox and search for X" — it proposes the steps, you confirm, it executes.

### Phase 7 — Safety & Sandboxing (hardening pass across everything built so far)
- Command allow/deny lists (block `rm -rf /`, `dd`, `mkfs`, writes to system paths, `chmod`/`chown` on protected dirs, fork bombs, etc.) — deny list checked *before* any shell execution, not just LLM-side reasoning.
- Route file-writing and code-execution actions through `bubblewrap` sandboxing where practical.
- Full audit log (timestamped record of every action proposed/approved/executed/denied).
- Rate limiting (e.g. max N actions per minute) to blunt any runaway loop.
- Global kill switch: hotkey and a spoken phrase ("Jarvis, stop") that immediately halts any in-flight action and clears the action queue.
- **Deliverable:** a security review pass with a written threat checklist, retrofitted onto Phases 4-6.

### Phase 8 — Caelestia-Native Overlay Widget
- Build a lightweight Quickshell/QML companion module that connects to the same backend daemon (WebSocket), for a minimal always-available visualizer/status bar element inside your actual Hyprland rice, separate from the full Tauri app window.
- **Deliverable:** optional slim overlay you can toggle, sharing state with the main app.

### Phase 9 — Polish
- Train a custom wake word (openWakeWord supports this) if "Jarvis" default doesn't fit well or you want a custom name.
- Upgrade TTS from Piper to Coqui XTTS-v2 for a more natural, expressive "premium assistant" voice (§2); offer 2-3 selectable voices in Settings.
- Latency tuning: streaming LLM tokens into TTS sentence-by-sentence rather than waiting for the full response, model quantization tuning, caching common responses.
- Session memory/context persistence.
- Plugin system so new tools can be added without touching core code.

---

## 6. Open Decisions to Confirm Before/During Build

1. **Backend language** — confirm Python default (§3) or prefer Rust from the start.
2. **Preferred wake word** — "Jarvis," or a custom name (custom requires a short training step in Phase 9, or we do it earlier if you want the real name from day one).
3. **Which free online providers** to wire up first in Phase 2 (Groq / OpenRouter / Gemini free tier) — can do more than one.
4. **Where the backend daemon lives** — plain background process launched by a fish function, or a proper `systemd --user` service for auto-start.
5. **Persona toggle** — should "sir" and the formal, dry-wit tone be always-on, or a switchable setting in case someone else uses the machine?

---

## 7. Honest Expectations

- **Latency:** With local Whisper + Ollama 7-8B + Piper all on your GPU/CPU, expect roughly 1-3 seconds wake-word-to-first-spoken-word for simple queries once Phase 9 streaming is in place; longer for tool-use chains (web search, multi-step screen actions). Online mode via Groq can be faster for the LLM step itself but adds network round-trip.
- **"Entirely free" caveat:** Every default component is free/open-source with no mandatory subscription. Cloud LLM *free tiers* have rate limits (requests/day, tokens/min) — fine for personal assistant use, but not unlimited. If you want zero limits, local-only mode has none (beyond your hardware).
- **This is a real software project**, not a weekend script — Phases 0-3 alone (working voice+text assistant with a real UI, no tools/screen/automation yet) is a legitimate milestone worth pausing at before deciding how far into Phases 4-8 to go.

---

*Next step: confirm the four open decisions in §5, then we start Phase 0.*
