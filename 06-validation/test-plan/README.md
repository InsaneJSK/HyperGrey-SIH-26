# Tests and reproduction

The project provides C++ regression groups, Python numerical/benchmark harnesses, API tests and package-integrity checks.

| Check | Entry point |
|---|---|
| Configure, build and run CTest | [Repository quick start](../../07-documentation/user-guide/quick-start.md) |
| C++ regression fixtures | [Solver tests](../../04-software/solver/tests/) |
| Numerical and benchmark harnesses | [Solver scripts](../../04-software/solver/scripts/) |
| API behavior | [Backend tests](../../04-software/backend/tests/) and [recorded verification](../../04-software/backend/VERIFICATION.md) |
| API smoke test | [Backend run instructions](../../04-software/backend/README.md) |
| Versioned experiment reproduction | [V2 reproduction guide](../../04-software/solver/docs/V2_REPRODUCE.md) and each [report](../../04-software/solver/reports/README.md) |
| Package and archive identities | [Validation guide](../README.md) |

Use the matching source snapshot and documented parameters for a historical experiment. Use a newly built executable and fresh output paths when evaluating the current source. The [Mac verification record](../readme-verification-2026-10-16.md) provides a concrete platform-specific build and test example.
