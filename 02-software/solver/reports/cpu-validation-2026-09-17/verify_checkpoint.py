"""Verify source/evidence identities and freeze the continuous-validation record.

Creates manifests only once. Later invocations verify the saved files without
rewriting either measured observations or frozen manifest identities.
"""
import ast
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def freeze(folder, scope):
    manifest_path = folder / "SNAPSHOT_MANIFEST.json"
    state_path = folder / "FINAL_STATE.json"
    if manifest_path.exists():
        manifest = read(manifest_path)
        for rel, digest in manifest.items():
            assert sha(folder / rel) == digest, str(folder / rel)
        assert read(state_path)["manifest_sha256"] == sha(manifest_path)
        return len(manifest)
    assert not state_path.exists()
    manifest = {p.relative_to(folder).as_posix(): sha(p)
                for p in sorted(folder.rglob("*"))
                if p.is_file() and "__pycache__" not in p.parts}
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    with state_path.open("x", encoding="utf-8") as stream:
        json.dump({"all_identity_checks_passed": True,
                   "manifest_sha256": sha(manifest_path),
                   "files": len(manifest), "scope": scope}, stream, indent=2)
        stream.write("\n")
    return len(manifest)


def main():
    experiment = ROOT / "reports/milp-iteration-29"
    state = read(experiment / "FINAL_STATE.json")
    manifest = read(experiment / "SNAPSHOT_MANIFEST.json")
    assert sha(experiment / "SNAPSHOT_MANIFEST.json") == state["snapshot_manifest_sha256"]
    for rel, digest in manifest.items():
        assert sha(experiment / rel) == digest, rel
    binary_hash = state["binary_sha256"]
    assert sha(ROOT / "build-milp-iter29/solver_cli.exe") == binary_hash
    assert read(experiment / "gate-local-runtime/SUMMARY.json")["all_pass"]
    results = BASE / "results"
    metadata = read(results / "metadata.json")
    assert metadata["binary_sha256"] == binary_hash
    assert sha(BASE / "run.py") == metadata["runner_sha256"]
    for rel, digest in metadata["source_sha256"].items():
        assert sha(ROOT / rel) == digest, rel
        assert sha(results / "source" / rel) == digest, rel
        assert sha(experiment / "final-source" / rel) == digest, rel
    for model in metadata["inputs"]:
        assert sha(results / model["snapshot"]) == model["input_sha256"]
    summary = read(results / "SUMMARY.json")
    assert summary["records"] == 37 and summary["unvalidated_native_completions"] == 0
    assert sha(results / "ledger.json") == summary["ledger_sha256"]
    study = BASE.parent / "lp-bandm-01"
    for subfolder, runner in [("results", "run.py"), ("lp-profile", "lp_profile.py")]:
        meta = read(study / subfolder / "metadata.json")
        assert meta["binary_sha256"] == binary_hash
        assert meta["runner_sha256"] == sha(study / runner)
    compact = read(study / "lp-profile/SUMMARY.json")
    assert compact["all_pass"] and compact["checked_completions"] == 16
    assert compact["ledger_sha256"] == sha(study / "lp-profile/ledger.json")
    for row in read(study / "lp-profile/ledger.json"):
        assert sha(Path(row["model"])) == row["model_sha256"]
    parsed = 0
    for folder in [ROOT / "scripts", BASE, study, experiment]:
        for path in sorted(folder.glob("*.py")):
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            parsed += 1
    smoke = experiment / "package-smoke"
    native = read(smoke / "production.stdout.log")
    wrapper = read(smoke / "production.json")
    reference = read(smoke / "production.reference.json")
    assert wrapper["status"] == "optimal" and wrapper["process_terminated"]
    assert native["objective"] == reference["objective"] == 420
    assert reference["candidate_checked"]
    assert reference["candidate_max_violation"] == reference["candidate_integer_violation"] == 0
    counts = {
        "iteration29_manifest_files": len(manifest),
        "source_files_verified": len(metadata["source_sha256"]),
        "python_files_parsed": parsed,
        "cpu_evidence_files": freeze(BASE, "37 current-source LP/QP observations, including failures and reference limits."),
        "lp_profile_evidence_files": freeze(study, "Six bandm diagnostics and one explicit 16/16 compact LP profile; defaults unchanged."),
        "smoke_evidence_files": freeze(smoke, "Same-host restricted-PATH launcher smoke; original-model checked objective 420. Not a fresh-OS install."),
    }
    print(json.dumps(dict(all_pass=True, binary_sha256=binary_hash, **counts), indent=2))


if __name__ == "__main__":
    main()
