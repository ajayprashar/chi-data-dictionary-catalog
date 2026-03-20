# How CMT ADT Data Quality Content Supports the Master Patient Effort

**Context:** CMT (Collective Medical Technologies, now PointClickCare) provides the ADT feed used in the data quality report. This document explains how that report and related CMT tables support the [Master Patient](https://www.notion.so/Master-Patient-30c5d66c407f80ee8edcfb95665ca280?pvs=21) effort and the **chi-data-dictionary-catalog** project ([repo](https://github.com/ajayprashar/chi-data-dictionary-catalog.git)).

---

## Summary

The CMT content helps in four ways:

1. **Populate and validate the ADT catalog** — The data quality report is a field-level inventory (Segment + HL7 Field → L2 column). It can drive or validate `ddc-hl7_adt_catalog.parquet` and link ADT fields to master patient `semantic_id`s.
2. **Source-specific feed profile** — Segment availability, fill rates, and “Recommended” (Mandatory / Good to have) describe what the CMT feed actually sends. That can live in a CMT feed profile (separate from the source-agnostic catalog).
3. **Governance and prioritization** — Fill rates, mandatory vs optional, and INV/SYN comments show which elements are critical for Master Patient and where there are open questions or deviations.
4. **Documentation and alignment** — Segment/event distribution and “expected but not received” segments (AL1, NK1, GT1) document real-world ADT usage for architects and interface teams.

---

## 1. Using the CMT Report to Populate or Validate the ADT Catalog

The project’s **ddc-hl7_adt_catalog.parquet** links:

- **ADT structure**: `segment_id`, `field_id` (e.g. PID-5, PV1-44), `field_name`, `data_type`, `optionality`, `cardinality`
- **Master Patient**: `semantic_id` (e.g. Patient.name_last, Patient.birth_date)
- **FHIR**: `fhir_r4_path`

The CMT **data quality report** provides:

| CMT report column   | Use in catalog / Master Patient |
|---------------------|----------------------------------|
| Source              | Identifies feed (e.g. CMT ADT)   |
| Segment             | Maps to `segment_id` (PID, PV1, PD1, IN1, DG1, PV2) |
| HL7 Field           | Maps to `field_id` (e.g. PID.5.1 → PID-5 component 1; PID.7.1 → PID-7) |
| INV Table (L2)      | Schema context (e.g. PD_ACTIVITY) |
| Column Name         | L2 column (e.g. LN, FN, DOB, RACE) — **link to semantic_id** via mapping |
| Display Name        | Human-readable name for `field_name` or documentation |
| Description        | Use in `notes` or dictionary text |
| Recommended        | Mandatory / Good to have — informs governance and validation rules |

**L2 column → semantic_id mapping (examples):**

- LN → Patient.name_last  
- FN → Patient.name_first  
- MN → Patient.name_middle  
- DOB → Patient.birth_date  
- GN → Patient.birth_sex (or gender)  
- RACE / RACEN → Patient race elements  
- PSA1, PCI, PST, PZ, PCY, PCT → Patient.address_*  
- TEL1 → Patient telecom  
- SSN → Patient identifier (SSN)  
- DOD, DF → Patient.death_date / deceased  
- ET, EID, EFDT, ELDT → Encounter.* (encounter-level; may map to Encounter resource, not only Patient)

Many CMT report rows are **encounter- or insurance-specific** (PV1, PV2, IN1, DG1). Those can still be added to the ADT catalog; encounter-related fields may map to an Encounter or other resources in the master model, or be documented as “ADT-only” until Master Patient expands to encounter-level semantics.

**Concrete step:** Build a mapping table (CSV or script) from **L2 Column Name** (and Segment + HL7 Field) to **semantic_id**. Then:

- Add rows to `ddc-hl7_adt_catalog.parquet` for each CMT field that has a semantic_id (or a new catalog element).
- Use CMT **Description** and **Observations** to fill `notes` and to document data quality context.

---

## 2. Source-Specific Feed Profile (CMT)

The catalog is **source-agnostic**: it describes ADT structure and links to Master Patient semantics. The CMT tables describe **one implementation**: what CMT actually sends.

Useful to capture in a **CMT feed profile** (separate doc or artifact):

- **Segment availability**  
  - Received: PID, PV1, PV2, PD1, IN1, DG1  
  - Expected per ACH but not received: AL1, NK1, GT1  

- **Event type distribution**  
  - A08 ~93%; A01, A02, A03 much lower — so “update” events dominate; useful for interface and validation design.

- **Per-field fill rates and quality**  
  - E.g. PID.5.3 (Middle Name) 77.53% fill; PID.10 (Race) 0% fill; many IN1/DG1 fields 0% — sets expectations for Master Patient survivorship and matching.

- **Mandatory vs optional (as implemented)**  
  - Mandatory fields with low fill (e.g. Encounter Type, Encounter ID, Discharge Disposition) and agreed handling (e.g. reject vs ingest as-is) from INV/SYN comments.

This profile does **not** change the structure of `ddc-hl7_adt_catalog.parquet`; it references the same segments/fields and adds CMT-specific metadata (e.g. “CMT sends this” / “CMT does not send this” / “Fill rate %”).

---

## 3. Governance and Prioritization

The CMT report supports Master Patient **governance**:

- **Mandatory** fields (e.g. PID.3, PID.5.1/5.2, PID.7, PV1 encounter fields) are the first candidates for Master Patient and for validation rules.
- **Good to have** fields with high fill (e.g. address, phone) inform which optional elements are worth including in survivorship and matching.
- **INV questions and SYN/ACH comments** document agreed behavior (e.g. default Address Type to HOME, ingest phone as received, how to handle missing Encounter Type/ID, DG1 code/name handling). That can feed into:
  - Data dictionary or business rules in the catalog/dictionary,
  - Or a separate “source agreements” or “deviations” doc referenced from the catalog.

---

## 4. Documentation and Alignment

- **Segment list (Data Received Y/N)**  
  Tells architects and interface engineers which segments exist in the CMT feed and which are missing (AL1, NK1, GT1). The ADT catalog can list all standard segments; the CMT profile notes which ones this feed uses.

- **Monthly file counts and event types**  
  Useful for capacity, monitoring, and which event types (A01/A02/A03/A08) to support in mapping and validation.

- **Master Patient link**  
  The same Master Patient semantics (and FHIR paths) used in this repo apply when consuming CMT ADT: CMT fields map to L2 columns, L2 columns map to semantic_ids, and semantic_ids tie to survivorship and Master Patient rules. The CMT report is the “real-world” view of one important ADT source for that effort.

---

## Implemented Next Steps

1. **L2 → semantic_id mapping**  
   For each CMT report row (or a subset focused on demographics and key encounter fields), decide the corresponding `semantic_id` (or note “no master element yet”). Use that to add or validate rows in `ddc-hl7_adt_catalog.parquet`.

2. **Add a CMT feed profile**  
   One markdown table or small CSV/Parquet under `docs/` or `data/`: segment availability, event type summary, and optionally per-field fill rate and “Recommended” from the report. Keep the main ADT catalog source-agnostic.

3. **Build script**  
   `python scripts/build_adt_catalog_from_mapping.py` — Reads the mapping CSV and writes **ddc-hl7_adt_catalog.parquet** in the project root. Run after editing the mapping. Options: `-m path/to/mapping.csv`, `-o path/to/output.parquet`.

4. **PRD**  
   **readme-prd.md** references the CMT feed, mapping, feed profile, and build script in Artifacts and Data pipeline.

---

## Table: CMT Report Columns → Catalog / Artifacts

| CMT report column        | Catalog / artifact use |
|--------------------------|-------------------------|
| Source                   | Tag as CMT ADT in feed profile |
| Segment                  | `segment_id` in ddc-hl7_adt_catalog |
| HL7 Field                | Parse to `field_id` (e.g. PID.5.1 → PID-5) |
| INV Table, Column Name   | L2 schema; Column Name → semantic_id mapping |
| Display Name, Description| `field_name`, `notes` |
| Recommended              | Governance; optionality / validation rules |
| Total Record, NULL, Fill %| CMT feed profile only (source-specific) |
| Observations, INV/SYN   | `notes` or deviation/agreement documentation |

This keeps the **catalog** as the single place for ADT structure and Master Patient links, and uses the **CMT content** to populate it, validate it, and document one key ADT source for Master Patient.
