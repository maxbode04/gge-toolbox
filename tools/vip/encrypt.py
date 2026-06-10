#!/usr/bin/env python3
"""Encrypt the VIP Corner pages (AES-256-GCM + PBKDF2-SHA256, decrypted in-browser
via WebCrypto). Same security model as StatiCrypt, but no Node — runs anywhere
Python + `cryptography` is installed.

Workflow (no-build friendly):
  1. Edit the *plaintext* pages in  tools/vip/_src/*.html   (gitignored — never pushed)
  2. Run:  python3 tools/vip/encrypt.py "ACCESS-CODE"
     (or set VIP_PASS env var and run with no args)
  3. It writes encrypted tools/vip/*.html (committed + served). The public repo
     only ever contains ciphertext for the VIP pages.

The password is NOT stored anywhere — only the salt, iteration count and
ciphertext land in the output. To change the code, just re-run with a new one.
"""
import os, sys, glob, base64, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_src")
ITERATIONS = 600_000  # OWASP-recommended for PBKDF2-SHA256

password = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VIP_PASS", "")).strip()
if not password:
    sys.exit("Usage: encrypt.py <access-code>   (or set VIP_PASS)")

# One salt per run → one derived key unlocks every page (seamless navigation).
salt = secrets.token_bytes(16)
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
key = kdf.derive(password.encode())
salt_b64 = base64.b64encode(salt).decode()

TEMPLATE = open(os.path.join(HERE, "_gate-template.html"), encoding="utf-8").read()

pages = sorted(glob.glob(os.path.join(SRC, "*.html")))
if not pages:
    sys.exit(f"No source pages in {SRC} — move the plaintext VIP html there first.")

for p in pages:
    name = os.path.basename(p)
    html = open(p, "rb").read()
    iv = secrets.token_bytes(12)               # fresh IV per page (never reuse with a key)
    ct = AESGCM(key).encrypt(iv, html, None)   # ciphertext includes the GCM tag
    payload = base64.b64encode(iv + ct).decode()
    out = (TEMPLATE
           .replace("{{SALT}}", salt_b64)
           .replace("{{ITER}}", str(ITERATIONS))
           .replace("{{PAYLOAD}}", payload))
    open(os.path.join(HERE, name), "w", encoding="utf-8").write(out)
    print(f"  encrypted {name}  ({len(html):,} → {len(payload):,} b64)")

print(f"\nDone — {len(pages)} pages encrypted with a fresh salt. Commit the *.html; keep _src local.")
