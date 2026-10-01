# Related: Data Curation via Standards

This repo is the **concept governance** half of the standards curation stack.

**Workspace file:** [`../data-curation-standards.code-workspace`](../data-curation-standards.code-workspace)

| Project | Path | Job |
| --- | --- | --- |
| **chiddc** (this repo) | `C:\AI\Incoming\chiddc` | Governed patient concepts: approval, USCDI / US Core, ADT / C-CDA / FHIR, curated value sets, partner crosswalk. Power BI + steward Excel. |
| **lookup-rollup** | `C:\AI\Incoming\lookup-rollup` | Published demographic **code extract** and lookup (`Src*` / `Map*` / `Rpt*`). Excel + HTML. |

Prefer consuming full code extracts from lookup-rollup for value-set members rather than rebuilding CDCREC twice. Do not merge the repos.

Git remote: `https://github.com/ajayprashar/chi-data-dictionary-catalog`
