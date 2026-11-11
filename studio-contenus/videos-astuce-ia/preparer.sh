#!/bin/sh
# Copie les polices, le logo et la photo du DG à côté de page.html, puis installe la voix (Kokoro) et le contrôle d'écoute.
set -e; cd "$(dirname "$0")"; A=../assets
mkdir -p polices; cp $A/logo/aite-consulting.png logo.png; cp $A/photos/veste-pied.webp dg.webp
for f in space-grotesk-latin-700 space-grotesk-latin-ext-700 ibm-plex-sans-latin-400 ibm-plex-sans-latin-500 ibm-plex-sans-latin-600 ibm-plex-sans-latin-ext-400 ibm-plex-sans-latin-ext-500 ibm-plex-sans-latin-ext-600; do cp $A/polices/$f-normal.woff2 polices/; done
[ -x .venv-tts/bin/python ] || { python3 -m venv .venv-tts; .venv-tts/bin/pip install -q kokoro-onnx soundfile faster-whisper numpy; }
[ -f package.json ] || echo '{"name":"videos-astuce-ia","private":true}' > package.json
