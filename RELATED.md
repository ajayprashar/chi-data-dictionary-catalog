# Related: Data Curation via Standards

This repo is the **governance product**. The sibling repo `lookup-rollup` is the **terminology factory**. Keep them separate. Do not merge the repos.

**Sibling:** `C:\AI\Incoming\lookup-rollup` (git remote `lookup-rollup`)  
**This repo’s remote:** `https://github.com/ajayprashar/chi-data-dictionary-catalog`  
**Longer decision brief** (outside both repos): [`../data-curation-standards.PROBLEM.md`](../data-curation-standards.PROBLEM.md)

“Code” means a terminology value (for example CDCREC `2106-3`), not software source. **CHI** (Community Health Insights) is the newer name for **SHIE**. Prefer CHI in new prose.

## What each repo owns

| Repo | Intent | What colleagues can open |
| --- | --- | --- |
| **chiddc** (this repo) | Govern CHI patient attributes on `semantic_id`: approval, USCDI / US Core, ADT / C-CDA / FHIR placement, a curated value-set subset, partner and county crosswalk. | Steward Excel (authors) and Power BI (readers) |
| **lookup-rollup** | Extract full demographic terminology from national publishers and keep it look-upable (`Src*` / `Map*` / `Rpt*`). | Excel workbook and a self-contained HTML lookup |

Shared topics: race, ethnicity, language, gender identity, birth sex. lookup-rollup also carries religion, nationality, marital status, sexual orientation, and null flavor. This repo’s pilot stays the five `semantic_id`s.

- This repo answers: *Which patient attributes does CHI govern, where do they appear in messages, and which partner or county values map to the chosen standard terms?*
- lookup-rollup answers: *What demographic terms did the national publisher define, and how might a term roll up for county reporting?*

Authoring here stays the steward workbook. Python imports that workbook to parquet. Power BI reads parquet. DuckDB and Jupyter are optional maintainer queries, not a colleague door.

## How work is allowed to move

Python, parquet, and markdown in this repo are the **personal factory**. Colleagues are not asked to open the repo, git, or an editor.

Approved colleague surfaces are **SharePoint**, **Excel (Microsoft 365)**, and **Power BI**. Notion is not an approved corporate home. Do not add Airtable or another database for the same facts.

The factory machine cannot reach SharePoint. Publishing is a manual copy over RDP into the work environment. SharePoint can hold an Excel snapshot and a short page written in that session. It does not host this repo’s Power BI project. The semantic model reads parquet from `C:\AI\Incoming\chiddc\`. Colleagues see a report only after Desktop on the work machine refreshes those files (or a `.pbix` that already imported them) and publishes to the Power BI service.

SharePoint co-authoring of the steward workbook stays deferred. Edits made there do not return to parquet unless the workbook is copied back. Day-to-day publish stays Excel → import → parquet → Power BI Desktop (`docs/operational-runbook.md`).

## Handoff that is still missing

Prefer consuming terminology members from the lookup-rollup extract for value-set members rather than rebuilding CDCREC here. This repo still holds a **subset**, not the full publisher list (`docs/crosswalk-model.md`). The feed from `master_demographics.csv` is **not wired**; local seed and HL7 expansion can drift from the extract.

Do not treat lookup-rollup `Map*` as this repo’s `Source_Value_Crosswalk`, or lookup-rollup `Rpt*` as county survivorship notes.
