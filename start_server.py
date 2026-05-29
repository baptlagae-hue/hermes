#!/usr/bin/env python3
"""Start the Expertise Transfer Engine backend server."""
import os, sys, subprocess, time, urllib.request, signal

# Read DEEPSEEK_API_KEY from .hermes/.env
key = None
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        line = line.strip()
        if line.startswith("DEEPSEEK_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

env = os.environ.copy()
if key:
    env["DEEPSEEK_API_KEY"] = key

print(f"Starting uvicorn... DEEPSEEK_API_KEY set: {bool(key)}")

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app",
     "--host", "127.0.0.1", "--port", "8010"],
    cwd="/root/expertise-transfer-engine",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

time.sleep(3)
try:
    resp = urllib.request.urlopen("http://127.0.0.1:8010/api/health")
    print(f"Health: {resp.read().decode()}")
    print("\nServer is running on http://127.0.0.1:8010")
    proc.wait()
except Exception as e:
    print(f"Error: {e}")
    proc.terminate()
    time.sleep(1)
    out = proc.stdout.read().decode() if proc.stdout else ""
    print("Output:", out[-800:])
