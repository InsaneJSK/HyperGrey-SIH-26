# 2. Install, build, test, and produce the results ZIP. Uses Kaggle's Python.
PUBLIC_TIME_LIMIT = 30
SIZES = [1000, 100000, 1000000]
REPEATS = 1  # Quick feedback first; repeated performance measurements can follow.

RUN = Path(tempfile.mkdtemp(prefix="run_", dir=WORK))  # Safe to rerun this cell.
LOGS = RUN/"run_logs"
LOGS.mkdir()
RESULTS = RUN/"reports"/"kaggle_validation"
stage = "setup"
status = {"completed": False, "gpu_enabled": False, "python": PYTHON}

try:
    # Standard system checks. No nvidia-smi is a CPU-only run, not a crash.
    gpu_ok = False
    if shutil.which("nvidia-smi"):
        hardware = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=30)
        (LOGS/"hardware.log").write_text(hardware.stdout+hardware.stderr, encoding="utf-8")
        gpu_ok = hardware.returncode == 0
    nvcc = shutil.which("nvcc")
    if not nvcc and Path("/usr/local/cuda/bin/nvcc").is_file():
        nvcc = "/usr/local/cuda/bin/nvcc"
    use_cuda = gpu_ok and bool(nvcc)
    status["gpu_enabled"] = use_cuda
    print("Mode:", "CPU + CUDA GPU" if use_cuda else "CPU ONLY (GPU or CUDA compiler unavailable)", flush=True)
    if not use_cuda:
        print("For GPU results: enable Settings > Accelerator > GPU, then Run All.", flush=True)

    configure = ["cmake", "-S", str(WORK), "-B", str(WORK/"build-v2"), "-DCMAKE_BUILD_TYPE=Release",
                 "-DSOVEREIGN_ENABLE_CUDA="+("ON" if use_cuda else "OFF")]
    if use_cuda:
        configure += ["-DCMAKE_CUDA_COMPILER="+nvcc]
        # Let CMake/compiler choose its default if capability querying is unavailable.
        capability = subprocess.run(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
                                    capture_output=True, text=True, timeout=30)
        caps = capability.stdout.strip().splitlines()
        if capability.returncode == 0 and caps and caps[0].replace(".", "").isdigit():
            configure += ["-DCMAKE_CUDA_ARCHITECTURES="+caps[0].replace(".", "")]

    validation = [PYTHON, str(WORK/"scripts/validate_v2.py"), "--output", str(RESULTS),
                  "--limit", str(PUBLIC_TIME_LIMIT), "--sizes", *map(str, SIZES),
                  "--repeats", str(REPEATS), "--scale-limit", "120"]
    if use_cuda:
        validation.append("--cuda")
    commands = [
        ("install", [PYTHON, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                     "highspy==1.12.0", "osqp==1.0.5", "numpy", "scipy", "psutil", "certifi", "nvidia-ml-py"]),
        ("versions", [PYTHON, "-m", "pip", "freeze"]),
        ("compiler", ["g++", "--version"]),
        ("configure", configure),
        ("build", ["cmake", "--build", str(WORK/"build-v2"), "-j", "2"]),
        ("parser_tests", [PYTHON, str(WORK/"scripts/test_result_parser.py")]),
        ("validation", validation),
    ]
    if use_cuda:
        commands.insert(3, ("cuda_version", [nvcc, "--version"]))
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
    print("Run finished. Known benchmark failures, if any, are retained in the report.")
except Exception:
    status["failed_stage"] = stage
    status["error"] = traceback.format_exc()
    print(status["error"])
    print("Send the ZIP below; it contains the error details so we can fix the next iteration.")
finally:
    (LOGS/"RUN_STATUS.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    destination = BASE/"sih26119_kaggle_results.zip"
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
