"""Download a declared Netlib subset and decompress with Netlib's data-only EMPS utility."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "datasets/netlib"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fetch(url, path):
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        if not data or data.lstrip().lower().startswith(b"<!doctype html"):
            raise RuntimeError(f"Unexpected download: {url}")
        path.write_bytes(data)

def main():
    selection = json.loads((TARGET / "selection.json").read_text())
    (TARGET / "raw").mkdir(parents=True, exist_ok=True)
    utility = ROOT / "tools/data/emps.c"
    utility.parent.mkdir(parents=True, exist_ok=True)
    fetch(selection["source"] + "emps.c", utility)
    fetch(selection["reference_values_source"], TARGET / "readme.txt")
    exe = ROOT / "build/emps.exe"
    exe.parent.mkdir(exist_ok=True)
    subprocess.run(["gcc", "-O2", str(utility), "-o", str(exe)], check=True)
    manifest = {"retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "utility_url": selection["source"] + "emps.c", "utility_sha256": sha(utility),
                "readme_sha256": sha(TARGET / "readme.txt"), "instances": []}
    for spec in selection["instances"]:
        name = spec["name"]
        raw, mps = TARGET / "raw" / name, TARGET / (name + ".mps")
        url = selection["source"] + name
        fetch(url, raw)
        decoded = subprocess.run([str(exe), str(raw)], capture_output=True, check=True)
        if b"ENDATA" not in decoded.stdout:
            raise RuntimeError(f"Invalid expanded MPS: {name}")
        mps.write_bytes(decoded.stdout)
        manifest["instances"].append({**spec, "url": url, "raw_sha256": sha(raw), "mps_sha256": sha(mps)})
        print(name, len(decoded.stdout), flush=True)
    (TARGET / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

if __name__ == "__main__":
    main()
