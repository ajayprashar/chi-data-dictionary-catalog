# Related: Data Curation via Standards

This repo is the **concept governance** half of the standards curation stack.

**Workspace file:** [`../data-curation-standards.code-workspace`](../data-curation-standards.code-workspace)  
**Cross-project note:** [`../data-curation-standards.RELATIONSHIP.md`](../data-curation-standards.RELATIONSHIP.md)

| Project | Path | Job |
| --- | --- | --- |
| **chiddc** (this repo) | `C:\AI\Incoming\chiddc` | Governed patient concepts: approval, USCDI / US Core, ADT / C-CDA / FHIR, curated value sets, partner crosswalk. Power BI + steward Excel. |
| **lookup-rollup** | `C:\AI\Incoming\lookup-rollup` | Extract and look up **demographic terminology** from national publishers (`Src*` / `Map*` / `Rpt*`). Excel + HTML. |

“Code” means a terminology value (e.g. CDCREC `2106-3`), not software source. **CHI** is the newer name for **SHIE** (see the relationship note).

Prefer consuming full terminology extracts from lookup-rollup for value-set members rather than rebuilding CDCREC twice. Do not merge the repos. Details: the relationship note above.

Git remote: `https://github.com/ajayprashar/chi-data-dictionary-catalog`
