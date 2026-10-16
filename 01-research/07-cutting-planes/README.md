# 07-cutting-planes

Cutting planes and cut management

## What this folder supports

Gomory/MIR, cover inequalities, cut validity, numerical safety and the tradeoff between stronger bounds and harder LPs.

**Problem-statement mapping:** PS-03, PS-09 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [docs/GOMORY_CUTS.md](../../02-software/solver/docs/GOMORY_CUTS.md)
- [docs/MILP_LIFTED_COVERS.md](../../02-software/solver/docs/MILP_LIFTED_COVERS.md)
- [docs/ADAPTIVE_CUT_ROUNDS.md](../../02-software/solver/docs/ADAPTIVE_CUT_ROUNDS.md)

## Scope note

The source repo's iteration 37 demoted Gomory cuts after end-to-end regressions; literature is not evidence to re-enable them.

## Sources (4; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2008 | Valid Inequalities for Mixed Integer Linear Programs | Mathematical Programming B 112, 3-44 | [PDF](2008-valid-inequalities-for-mixed-integer-linear-programs.pdf) / [note](2008-valid-inequalities-for-mixed-integer-linear-programs.source.md) | [source](https://www.andrew.cmu.edu/user/gc0v/) |
| 2023 | Safe and Verified Gomory Mixed Integer Cuts in a Rational MIP Framework | arXiv preprint | [PDF](2023-safe-and-verified-gomory-mixed-integer-cuts-in-a-rational-mip-framework.pdf) / [note](2023-safe-and-verified-gomory-mixed-integer-cuts-in-a-rational-mip-framework.source.md) | [source](https://arxiv.org/abs/2303.12365) |
| 2025 | New Sequence-Independent Lifting Techniques for Cover Inequalities and When They Induce Facets | IJCAI 2025 | [PDF](2025-new-sequence-independent-lifting-techniques-for-cover-inequalities-and-when-they-induce-facets.pdf) / [note](2025-new-sequence-independent-lifting-techniques-for-cover-inequalities-and-when-they-induce-facets.source.md) | [source](https://www.ijcai.org/proceedings/2025/298) |
| 1998 | Lifted Cover Inequalities for 0-1 Integer Programs: Computation | INFORMS Journal on Computing 10(4), 427-437 | [note](1998-lifted-cover-inequalities-for-0-1-integer-programs-computation.source.md) / reference only | [source](https://doi.org/10.1287/ijoc.10.4.427) |

## Reading notes

- **valid-inequalities:** Mathematical basis for GMI, MIR, split and lift-and-project inequalities and their relationships.
- **safe-gmi:** Directed rounding and certificate checks show how cut validity can survive finite-precision computation.
- **cover-lifting:** Study cover generation and strengthened lifting, with explicit validity assumptions.
- **classic-lifted-cover:** Canonical computational reference for separating and lifting binary knapsack cover inequalities.

[Back to the research index](../README.md)
