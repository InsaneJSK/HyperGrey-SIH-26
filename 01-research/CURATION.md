# Collection and verification record

Curated on **2026-09-27** for the software problem statement **SIH26119**. This collection follows the numbered research folders, topic READMEs, citation tables and dated PDF names in the separate `Hyper-Grey-SIH-26` hardware repository. Topics and sources were selected independently for this software project.

## Coverage and selection

The library contains **60 sources across 15 topics: 43 local PDFs and 17 reference-only entries**. It combines foundational papers, recent algorithm research, official technical documentation, benchmark descriptions, industrial formulations and an MRPL annual report. The [research map](RESEARCH_MAP.md) explains priorities and connects the collection to the supplied problem statement and existing solver evidence.

Primary author, university, publisher, institutional, benchmark and official documentation sites were preferred. Relevance was assessed against the mathematical core, numerical reliability, sparse computation, GPU/multicore work, evaluation and industrial examples. The collection is a starting bibliography, not a systematic review or a claim that the newest source has been found in every area.

## Checks performed

- Checked bibliographic identity and downloaded PDF front matter; recorded differences between preprints, technical reports, final publications and documentation versions in the source notes.
- Parsed all held PDFs, recorded their page counts and checked for duplicate file contents. The downloaded files are unmodified originals.
- Recorded retrieval time, download location, file size and SHA-256 in [retrieval.json](retrieval.json).
- Visually checked the title pages of the two MIT lecture notes, *Geometry of Linear Programming* and *Duality Theory*: their text extraction has font-encoding problems, but the rendered pages are legible.
- Checked local Markdown links, catalog coverage and file integrity with the offline maintenance tool. The latest result is [VALIDATION.json](VALIDATION.json).

These checks establish file identity, readability at the inspected pages and organization. They do not constitute a full technical review of every paper, independent reproduction of results, or endorsement of every proposed technique. External links can change after the retrieval date.

## Reference-only entries and access limits

Sixteen sources are intentionally linked rather than mirrored, including books, living documentation, benchmark portals and publisher references. A seventeenth, *Presolve Reductions in Mixed Integer Programming*, remains citation-only after its public full-text location could not be retrieved as a valid PDF. One retrieval encountered a certificate failure; a separate request with normal certificate validation returned an HTML challenge page. No HTML response was stored as a PDF.

A failed scripted landing-page request is disclosed in the relevant note even when a separate legitimate PDF location succeeded. The [source catalog](catalog.json) and retrieval record distinguish selected sources, successful downloads and unavailable full text.

## Citation and reuse

Use each topic README for browsing and each `.source.md` note for citation, relevance, version and access details. [references.bib](references.bib) contains all 60 citations. Filenames normally use the final citation year; living documentation uses the access year. The held version can have a different date, documented in its note.

Public access alone is not a general redistribution license. Retain source notices and consult the linked rights information for any reuse. Original relevance notes summarize why the source matters to this project; they do not reproduce source abstracts.

[Back to the research index](README.md)
