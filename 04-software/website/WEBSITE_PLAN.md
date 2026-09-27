# SIH26119 website plan

Prepared 17 September 2026. Planning only; this does not resume solver development or authorize deployment. Assumption: the first audience is SIH judges and technical evaluators, followed by industrial analysts and developers.

## Product direction

Build a browser-based optimization workbench with a concise public introduction. Its central story is: choose an industrial problem, inspect its inputs, run our solver, understand the decision and inspect the evidence supporting it.

The supplied PS explicitly prioritizes a solver built from mathematical foundations, numerical robustness, benchmarks and an API/CLI. The website should make these strengths demonstrable. Scope the first release around a reliable demonstration, with the existing C++ engine doing the optimization.

Working label: **Sovereign Solver**. Final product/team name, logo and domain are still open.

## Existing assets and integration gaps

| Available now | Website work required |
|---|---|
| C++ solver and JSON CLI output | HTTP API, normalized result schema and isolated job runner |
| MPS, QPLIB and lpmini input paths | Upload validation, supported-format guidance and model inspection |
| LP, MILP and supported continuous convex QP methods | Capability-aware controls and accurate status explanations |
| CUDA box-QP path | Availability detection; GPU evidence screen; live GPU optional |
| Four industrial MPS examples with source manifest | Named inputs, units, scenario forms and decision visualizations |
| Retained benchmark reports and validation artifacts | Curated, versioned evidence index and comparison views |
| Final traces and JSON results | Job lifecycle polling initially; streaming solver telemetry is separate work |

Evidence comes from `04-software/solver/Problem Statement.txt`, `docs/V2_ARCHITECTURE.md`, `docs/INDUSTRIAL_CASES.md`, `src/main.cpp` and the current iteration24 assessment. Some historical reports concern older binaries; they must retain their original identities.

## Pages and priority

### 1. Overview — MVP

One clear message: an indigenous optimization engine for industrial planning. Explain LP, MILP and convex QP in plain language, show an authentic application screen and offer **Try an example**, **Open workspace**, and **View evidence**. Include current support, architecture, method provenance and source/download documentation. Avoid unsupported speed, industrial-readiness or licensing-cost claims.

### 2. Solver workspace — MVP, highest priority

Flow: example or upload → validate/inspect model → choose supported settings → solve → inspect/export result.

- Inputs: supported `.mps`, `.qplib`, `.lpmini` files; launch industrial templates directly. Document parser limitations instead of promising full support for every format dialect.
- Inspection: model type, rows, columns, nonzeros, integer variables, objective direction, bounds and unsupported features.
- Basic settings: time allowance, applicable gap/tolerance, supported CPU thread options. Keep a small allowlist of release profiles; experimental flags belong in documented research evidence.
- GPU selection appears only when the model and execution host support it. Report the actual backend used.
- Run experience: queued/running/checking/finished states, elapsed time and cancellation. A timer is elapsed time, not percentage completed.
- Result: checked solution availability, termination reason, objective, valid bound/gap where supplied, solve time and end-to-end time, feasibility/integrality checks, variable table and downloadable artifacts.
- Missing metrics display **Unavailable**, never zero. Show approximate numerical completion separately from restricted exact proof.
- Export original/modified input, solution CSV, normalized JSON, solver output, validation summary, options, version and hashes. Add a printable report before custom PDF generation.
- A compact run list lives in the workspace; a separate history page can follow later.

### 3. Industrial examples — MVP with one polished case

**Flagship: refinery planning and blending.** Use the retained MARCO literature model and its tighter sulfur scenario. Inputs should use domain names and source units. Show crude purchases, process use, product output, binding or nearly binding constraints, and profit. Our emitted objective is cost minus revenue, so the presentation must explicitly map negative objective to positive profit. Preserve the source's historical currency and units.

What-if demonstration: solve the 3.5 fuel-oil sulfur limit, tighten it to 3.4, rerun, and compare the actual checked plans. A tighter feasible set cannot improve the true optimal profit; incomplete/numerical results require appropriate interpretation. Display observed values, not invented savings. Treat this as a literature teaching case, not MRPL operating data.

**Transportation:** existing two-plant, three-market case; show shipment allocation and total cost with capacities/demand. Good for a fast, easily understood first run.

**Production:** existing synthetic six-period MILP; show production, inventory and setup decisions on a period chart. Display open gaps if the run stops early.

**Supported QP/GPU:** optional separate example and recorded hardware comparison. Broader power-dispatch demonstrations require a validated template before being advertised.

Scenario edits must rebuild model data deterministically, preserve baseline and changed inputs, and rerun verification. Arbitrary spreadsheet import and natural-language model generation are outside the MVP.

### 4. Benchmark evidence — MVP

Curate recorded runs from recognized datasets. Each row should expose dataset/model, class and size, solver build/profile, hardware/backend, limits/tolerances, objective, bound/gap, elapsed time and validation outcome. Include failures and timeouts.

Provide drill-down to provenance, raw results and reproduction command. Comparisons need matched conditions before being presented as speed comparisons. Existing short reference runs used to validate answers must retain that label.

Current iteration24 evidence is an **experimental, off-by-default profile on 27 reused development models**: 25 checked feasible points plus one cross-checked infeasible case; ten completions, fifteen feasible open gaps and one model without a point. Do not convert 26/27 useful outcomes into 26 optimal solutions or a default-profile result.

CPU/GPU comparisons must identify supported workload, hardware, accuracy, repetitions and timing boundaries. A large box-QP experiment does not establish equivalent LP/MILP scalability.

### 5. Developer documentation — MVP, compact

Quick start, supported input contract, CLI and planned HTTP API examples, status meanings, methods/architecture, reproducibility, limitations and known unsupported classes. Describe the existing C++ API separately from the HTTP API we will add. Keep HiGHS/OSQP reference-validation dependencies separate from the core engine.

## Visual direction

- Desktop-first engineering workspace; responsive overview and usable stacked controls on phones.
- Off-white/light or charcoal/dark surfaces, deep navy structure, restrained teal actions; amber for incomplete outcomes and red for errors. Status always includes text.
- Left navigation, compact top bar, model/scenario title, inputs alongside results and expandable technical detail.
- Use clear tables, meaningful plots and ample spacing. Use monospaced text for model identifiers and numerical diagnostics.
- Charts should answer specific questions: how did the objective/bound evolve, what changed between scenarios, which capacity is binding, which route carries how much?
- Keyboard-accessible forms, readable contrast, clear units and errors adjacent to the relevant input.
- Public overview should lead with the industrial purpose and an authentic workspace preview. No unsupported headline statistics.

## Proposed technical structure

```text
React + TypeScript + Vite interface
                |
          Python FastAPI
                |
        persisted job queue
                |
       isolated worker process
                |
       frozen C++ solver CLI
                |
   result checks + retained artifacts
```

Recommendation: use React/TypeScript/Vite for the interface, FastAPI for model/job endpoints, and the current executable through an argument-array subprocess adapter. This is a proposal; there is no existing website scaffold to preserve.

For a local demonstration, use SQLite for job metadata, a task-owned artifact directory and one worker. For shared hosting, use a persistent CPU server/container, a durable queue and concurrency/resource limits. PostgreSQL and Redis-backed workers become useful when multiple users/workers justify them; they are not prerequisites for the local MVP. The static UI can be served with the API or separately.

Long solves must run outside request handling. FastAPI's documentation recommends separate tools/processes for heavy computation: https://fastapi.tiangolo.com/tutorial/background-tasks/#caveat. Vite documents static frontend builds/deployment: https://vite.dev/guide/static-deploy.html.

A public web host does not automatically supply a C++ compute worker or GPU. Start with local CPU execution and a portable local demo. Recorded Kaggle GPU results can be displayed with source and hardware labels; Kaggle notebooks are not the live website backend. Live GPU service requires a separate supported host and budget.

### Proposed API contract

- `GET /capabilities`: build identity, supported formats/classes, available backends and limits.
- `GET /examples`: template metadata, sources, editable fields and units.
- `POST /models`: bounded upload or template parameters; return model ID and inspection/errors.
- `POST /runs`: model ID and allowlisted settings; return a queued job ID.
- `GET /runs/{id}`: lifecycle and normalized result metadata.
- `POST /runs/{id}/cancel`: cancel queued work or terminate the active process tree.
- `GET /runs/{id}/artifacts/{name}`: authorized download from a fixed artifact inventory.
- `GET /benchmarks`: curated recorded evidence.

Use polling first. If later adding SSE, emit genuine solver events; current final JSON and final traces do not provide a live convergence feed by themselves.

### Result and execution requirements

Keep job lifecycle, solver termination, solution verification and optimality/proof status as separate fields. A process ending is not evidence of optimality. A nonzero CLI exit code can accompany a useful limit result; parse valid structured output before classifying it. Preserve raw status and diagnostics.

Record model hash, solver binary/source identity, options, profile, backend/hardware, timestamps, input units, original objective sense/offset, solution availability and verification status. Scope gap/bound semantics by model family; QP and MILP metrics are not interchangeable.

For hosted uploads, set size/model limits, server-generated paths, command-option allowlists, job isolation, process-tree cancellation, wall-time/memory caps, per-session ownership and rate/concurrency limits. Retain only explicit artifacts and define cleanup. A forced kill may have no final JSON; report interruption honestly and use partial solutions only if actually retained and checked. Public uploads require these controls before release.

## What the team needs

1. A chosen product name, simple visual identity and short project description; a domain is optional for the first demo.
2. One frozen solver build/profile with a documented supported-input contract and small dependable example set.
3. A stable result adapter and model-inspection path, independent point checks and a capabilities endpoint.
4. Source-backed labels, units and editable parameter mappings for the refinery scenario; a domain review improves the industrial story.
5. A curated evidence bundle with raw results, dataset permissions/provenance, hardware and build metadata.
6. A frontend implementer, API/worker implementer and solver/domain reviewer. These are responsibilities and can be shared.
7. A local demo machine, optional CPU hosting account, and a separately decided GPU hosting budget if live GPU execution is needed.
8. A scripted demonstration and clearly labeled saved-run/recording fallback that works without internet.

## Implementation order and estimate

Rough estimate: **7–10 focused person-days** for the MVP, assuming the existing solver is frozen and suitable demo cases work. This is an effort estimate, not a calendar commitment; it excludes new solver algorithms, live GPU hosting and a full modeling editor.

| Phase | Deliverable | Estimated effort |
|---|---|---|
| 1 | Confirm supported demo profile, input/result contract and screen flows | 0.5–1 day |
| 2 | Local API, isolated worker, upload/inspection, cancellation and artifact storage | 2–3 days |
| 3 | Workspace and one complete solve/result/export flow | 1.5–2 days |
| 4 | Refinery what-if and curated benchmark evidence | 1.5–2 days |
| 5 | Overview/docs, accessibility, deployment packaging and demo rehearsal | 1–2 days |

After agreeing the contract, frontend work with labeled fixtures and API work can proceed concurrently. Integrate real execution early. Defer accounts/team administration, billing, chatbots, a generic visual model builder, arbitrary Excel ingestion, animated branch trees and live GPU scheduling.

## Acceptance criteria

- A visitor can open a bundled case, inspect it, run the actual engine and download a checked result.
- Baseline and changed refinery inputs produce separately retained runs and a truthful comparison.
- Feasible-at-limit, no-point-at-limit, infeasible, unsupported, malformed input and cancellation render correctly.
- Unsupported GPU selection is unavailable or clearly rejected; the actual backend is recorded.
- Benchmarks link to their actual build/configuration and never blend results from different profiles into one score.
- Concurrent requests queue within limits; cancellation terminates child processes and frees capacity.
- No endpoint can read arbitrary files, execute arbitrary flags or expose another session's uploads.
- A clean machine can start the local demo from documented steps; an offline rehearsal succeeds.
- First release includes one complete industrial flow, an honest benchmark view, and a compact developer guide.

## Suggested judge demonstration

Open refinery planning → explain the literature model and source units → solve baseline → inspect output and feasibility checks → tighten sulfur from 3.5 to 3.4 → solve and compare actual decisions/profit → open one benchmark record and reproduction details → show supported GPU evidence separately. Finish by demonstrating that a limit or unsupported model produces an accurate status.

The MARCO scenario is supported by the repository's industrial documentation and the original model: https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html.
