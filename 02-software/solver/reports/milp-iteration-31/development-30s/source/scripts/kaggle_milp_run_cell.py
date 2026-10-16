# 2. Focused hard-MILP comparison. CPU only; no GPU quota required.
MILP_ONLY = True
EXPERIMENT = "branching"
SECONDS_PER_CASE = 180
NODE_LIMIT = 250000
REFERENCE_SECONDS = 30

RUN = Path(tempfile.mkdtemp(prefix="milp_run_", dir=WORK))
LOGS = RUN/"run_logs"
LOGS.mkdir()
RESULTS = RUN/"reports"/"milp_focus"
stage = "setup"
status = {"completed": False, "gpu_enabled": False, "profile": "milp_focus", "experiment": EXPERIMENT, "python": PYTHON}

try:
    print("CPU-only MILP experiment: 3 models x 2 strategies x 180 seconds maximum.", flush=True)
    print("Experiment:", EXPERIMENT, flush=True)
    print("Allow about 20-25 minutes including installation, checks and reference runs.", flush=True)
    commands = [
        ("install", [PYTHON, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                     "highspy==1.12.0", "numpy", "psutil", "certifi"]),
        ("versions", [PYTHON, "-m", "pip", "freeze"]),
        ("compiler", ["g++", "--version"]),
        ("configure", ["cmake", "-S", str(WORK), "-B", str(WORK/"build-milp-focus"),
                       "-DCMAKE_BUILD_TYPE=Release", "-DSOVEREIGN_ENABLE_CUDA=OFF"]),
        ("build", ["cmake", "--build", str(WORK/"build-milp-focus"), "-j", "2"]),
        ("parser_tests", [PYTHON, str(WORK/"scripts/test_result_parser.py")]),
        ("validation", [PYTHON, str(WORK/"scripts/validate_milp_focus.py"), "--output", str(RESULTS),
                        "--limit", str(SECONDS_PER_CASE), "--nodes", str(NODE_LIMIT),
                        "--reference-limit", str(REFERENCE_SECONDS), "--experiment", EXPERIMENT]),
    ]
    for stage, command in commands:
        print("Running:", stage, flush=True)
        log_path = LOGS/(stage+".log")
        with log_path.open("w", encoding="utf-8") as log:
            result = subprocess.run(command, cwd=WORK, stdout=log, stderr=subprocess.STDOUT, timeout=3600)
        if stage != "versions":
            print(log_path.read_text(encoding="utf-8", errors="replace")[-6000:], flush=True)
        if result.returncode != 0:
            raise RuntimeError(f"{stage} exited with code {result.returncode}; see run_logs/{stage}.log")
    summary = json.loads((RESULTS/"summary.json").read_text())
    status["completed"] = True
    print(json.dumps(summary, indent=2))
    print("Comparison finished. Unsolved hard cases remain in the results.")
except Exception:
    status["failed_stage"] = stage
    status["error"] = traceback.format_exc()
    print(status["error"])
    print("Send the ZIP below even if this run failed.")
finally:
    (LOGS/"RUN_STATUS.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    destination = BASE/"sih26119_milp_results.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder in (LOGS, RESULTS):
            if folder.exists():
                for path in sorted(folder.rglob("*")):
                    if path.is_file():
                        archive.write(path, path.relative_to(RUN).as_posix())
        for name in ("SOURCE_MANIFEST.json", "SNAPSHOT.json"):
            if (WORK/name).is_file():
                archive.write(WORK/name, name)
    os.chdir(BASE)
    print("DOWNLOAD AND SEND BACK:", destination)
    display(FileLink(destination.name))
