"""Prepare explicitly selected MIPLIB and QPLIB originals, with provenance hashes."""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SELECTION = {
    "miplib": [(n, f"https://miplib2010.zib.de/miplib3/miplib3/{n}.mps.gz") for n in ["p0033", "enigma", "flugpl", "stein27"]],
    "qplib": [(n, f"https://qplib.zib.de/qplib/QPLIB_{n}.qplib") for n in ["8792", "8991", "9002"]]
}

def download(url, path):
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response: data = response.read()
        path.write_bytes(data)
    return path.read_bytes()

def main():
    for family, selected in SELECTION.items():
        folder = ROOT/"datasets"/family
        (folder/"raw").mkdir(parents=True, exist_ok=True)
        records = []
        for name, url in selected:
            raw = folder/"raw"/url.rsplit("/",1)[-1]
            data = download(url, raw)
            expanded = gzip.decompress(data) if family == "miplib" else data
            model = folder/(name+(".mps" if family == "miplib" else ".qplib"))
            model.write_bytes(expanded)
            record = {"name": name, "url": url, "raw_sha256": hashlib.sha256(data).hexdigest(),
                      "model_sha256": hashlib.sha256(expanded).hexdigest()}
            if family == "qplib":
                lp_url = f"https://qplib.zib.de/lp/QPLIB_{name}.lp"
                lp = folder/(name+".lp")
                lp_data = download(lp_url, lp)
                record.update(reference_url=lp_url, reference_sha256=hashlib.sha256(lp_data).hexdigest())
            records.append(record)
            print(family, name, len(expanded), flush=True)
        (folder/"manifest.json").write_text(json.dumps({
            "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "policy": "Predeclared first-version smoke subset; all attempts retained. MIPLIB instances are historical 3.0, not 2017.",
            "instances": records}, indent=2)+"\n")

if __name__ == "__main__": main()
