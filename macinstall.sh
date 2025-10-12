#!/usr/bin/env bash
set -euo pipefail
SRC="fssh.py"

if [ ! -f "$SRC" ]; then echo "error: fssh.py not found" >&2; exit 1; fi
PY="$(command -v python3 || true)"

if [ -z "$PY" ]; then echo "error: python3 not found" >&2; exit 1; fi
VENV_DIR="/usr/local/fssh"
LAUNCHER="/usr/local/bin/fssh"

if [ ! -d "$VENV_DIR" ]; then sudo mkdir -p "$VENV_DIR"; sudo chown "$(id -un)" "$VENV_DIR"; fi
"$PY" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

if command -v brew >/dev/null 2>&1; then brew install openssl@3 pkg-config rust || true; OPENSSL_PREFIX="$(brew --prefix openssl@3 2>/dev/null || true)"; if [ -n "$OPENSSL_PREFIX" ]; then export LDFLAGS="-L$OPENSSL_PREFIX/lib"; export CPPFLAGS="-I$OPENSSL_PREFIX/include"; export PKG_CONFIG_PATH="$OPENSSL_PREFIX/lib/pkgconfig"; fi; fi
"$VENV_DIR/bin/python" -m pip install paramiko PyYAML
install -m 755 "$SRC" "$VENV_DIR/fssh.py"
"$VENV_DIR/bin/python" - "$VENV_DIR/fssh.py" <<'PY'

import sys,re
p=sys.argv[1]
s=open(p,'r',encoding='utf-8').read()
s=re.sub(r"(?m)^\s*CONF\s*=.*$","CONF = os.path.expanduser(\"~/.fssh.yaml\")",s)
open(p,'w',encoding='utf-8').write(s)

PY
TMP="$(mktemp)"
cat >"$TMP" <<'EOF'
#!/usr/bin/env bash
exec /usr/local/fssh/bin/python /usr/local/fssh/fssh.py "$@"
EOF

sudo mv "$TMP" "$LAUNCHER"
sudo chmod +x "$LAUNCHER"
echo "installed: venv -> $VENV_DIR, launcher -> $LAUNCHER"
