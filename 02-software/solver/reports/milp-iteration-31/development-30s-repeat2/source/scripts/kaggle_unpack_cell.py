# 1. Load the companion source ZIP attached as a Kaggle input dataset.
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, tempfile, traceback, zipfile
from IPython.display import display, FileLink

BASE = Path("/kaggle/working") if Path("/kaggle/working").is_dir() else Path.cwd()
INPUT = Path("/kaggle/input") if Path("/kaggle/input").is_dir() else BASE/"input"
WORK = Path(tempfile.mkdtemp(prefix="sih26119_", dir=BASE))
PYTHON = sys.executable
SNAPSHOT_SHA256 = "__SNAPSHOT_SHA256__"
MANIFEST_SHA256 = "__MANIFEST_SHA256__"
loaded = False

# Accept either the uploaded ZIP or files already unpacked by the dataset upload.
for source_zip in sorted(INPUT.rglob("SIH26119_V2_source.zip")):
    if hashlib.sha256(source_zip.read_bytes()).hexdigest() != SNAPSHOT_SHA256:
        continue
    with zipfile.ZipFile(source_zip) as archive:
        for entry in archive.infolist():
            if WORK.resolve() not in (WORK/entry.filename).resolve().parents:
                raise RuntimeError("Unsafe archive path")
        archive.extractall(WORK)
    loaded = True
    break
if not loaded:
    for marker in sorted(INPUT.rglob("SOURCE_MANIFEST.json")):
        if hashlib.sha256(marker.read_bytes()).hexdigest() != MANIFEST_SHA256:
            continue
        source_root = marker.parent.resolve()
        for name in json.loads(marker.read_text(encoding="utf-8")):
            source = (source_root/name).resolve()
            target = (WORK/name).resolve()
            if source_root not in source.parents or WORK.resolve() not in target.parents:
                raise RuntimeError("Unsafe dataset path")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        shutil.copy2(marker, WORK/"SOURCE_MANIFEST.json")
        loaded = True
        break
if not loaded:
    raise FileNotFoundError(
        "Attach the NEW SIH26119_V2_source.zip as a Kaggle input dataset, then Run All. "
        "The dataset name does not matter. An older ZIP will not match this notebook."
    )

manifest_path = WORK/"SOURCE_MANIFEST.json"
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == MANIFEST_SHA256
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for name, expected in manifest.items():
    assert hashlib.sha256((WORK/name).read_bytes()).hexdigest() == expected, "Source changed: "+name
(WORK/"SNAPSHOT.json").write_text(json.dumps({"snapshot_sha256": SNAPSHOT_SHA256}, indent=2))
os.chdir(WORK)
assert Path("scripts/test_result_parser.py").is_file()
print("Working directory:", Path.cwd())
print("Python:", PYTHON)
print("Source verified. Now run the next cell.")
