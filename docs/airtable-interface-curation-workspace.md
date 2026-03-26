# Airtable Interface Build Guide (Fast Path Style)

This version uses the same format you preferred: short, step-by-step, click-by-click.

## Before You Start (2 minutes)

1) Confirm latest sync (optional but recommended)
- Run:
```powershell
python scripts\upload_parquet_to_airtable.py --include-standards-inventories --add-relations
```

2) Build these pages in order
- Page A: Semantic Hub
- Page B: HL7 ADT Lookup
- Page C: CCDA Lookup
- Page D: Curation Queues

3) Ground rules
- `semantic_id` is your core key for meaning.
- `Name` is display only; in `ddc-hl7_adt_catalog` keep it compact for steward scanning.
- `upsert_key` is technical (hide for stewards).
- This interface guide assumes partner intake stays outside the steward base.
- Build these pages over the curated `ddc-*` governance and lookup tables only.

4) Table groups in the current base
- Core governance:
  - `ddc-master_patient_catalog`
  - `ddc-master_patient_dictionary`
  - `ddc-business_rules`
- Interoperability lookup/reference:
  - `ddc-hl7_adt_catalog`
  - `ddc-ccda_catalog`
  - `ddc-fhir_inventory`
- Operational reference:
  - `ddc-data_source_availability`

---

## Page A: Semantic Hub (click-by-click)

Title: `Semantic hub`  
Purpose: Steward governed concepts by `semantic_id`, review implementation detail, and jump to related catalog context.  
Data source: `ddc-master_patient_dictionary` (primary) + related `ddc-master_patient_catalog`.

Build order (fast path)

1) Page shell
- Open your Interface page `Semantic hub`.
- Keep the top Text block.
- Title it: `Semantic Hub`.
- Add one sentence:
  - `Browse canonical elements and open full dictionary/FHIR curation detail by semantic_id.`

2) Main element list (dictionary primary)
- Click `Add element` -> `List`.
- Source: `ddc-master_patient_dictionary`.
- Element title: `Find an Element (Dictionary)`.
- In list settings:
  - Sort: `semantic_id` ascending.
  - Group: none.
  - Show fields/columns (in this order):
    - `semantic_id`
    - `fhir_r4_mapping_readiness`
    - `standards_curation_readiness`
    - `fhir_r4_path`
    - `fhir_profile`
- Turn on `Click into record details` (or equivalent open-on-click).

3) Add user filters (top of list)
- Source: `ddc-master_patient_dictionary` (the main list on Page A).
- In the same list’s filter controls, add:
  - `fhir_r4_mapping_readiness`
  - `standards_curation_readiness`
  - Text filter: `semantic_id` contains
  - Text filter: `fhir_r4_path` contains
- Keep these as user-adjustable controls, not hard-coded conditions.

4) Record detail panel for dictionary
- In list/detail settings, show:
  - `semantic_id`, `fhir_r4_path`, `fhir_data_type`, `fhir_profile`
  - `fhir_cardinality`, `fhir_must_support`
  - `chi_survivorship_logic`, `data_source_rank_reference`
  - `fhir_r4_mapping_readiness`, `fhir_r4_mapping_gap_details`
  - `standards_curation_readiness`, `standards_curation_gap_details`
- Hide technical fields not needed for stewards (`upsert_key`).

5) Wire Grid 1 -> Grid 2 context (required)
- Goal: selecting a row in Grid 1 (`ddc-master_patient_dictionary`) automatically scopes Grid 2 (`ddc-master_patient_catalog`).
- This only works when Grid 1 exposes a `Selected record` context variable.

Pattern A (recommended): selected-record variable filter
- Select Grid 1 and confirm row click sets selection:
  - In right panel, enable the behavior equivalent to `Select record on click`.
  - Keep `semantic_id` visible in Grid 1.
- Add Grid 2 as a `List` or `Record list`.
- Source: `ddc-master_patient_catalog`.
- Select Grid 2 -> right panel -> `Data` -> `Filter` -> `Add condition`.
- Configure condition:
  - Field: `semantic_id`
  - Operator: `is` / `equals`
  - Value: `Insert variable` -> `Selected record from <Grid 1>` -> `semantic_id`
- Expected result: Grid 2 instantly updates when a different Grid 1 row is selected.
- Show catalog fields:
  - `semantic_id`, `uscdi_element`, `uscdi_description`
  - `uscdi_data_class`, `uscdi_data_element`
  - `approval_status`, `data_steward`, `domain`

Pattern B (more reliable in newer Interface layouts): record review + related data
- Add a `Record review` (or detail) element for `ddc-master_patient_dictionary`.
- Set the page context to `Selected record`.
- Add a second element tied to related catalog context using that selected record:
  - either a filtered `List` of `ddc-master_patient_catalog` with `semantic_id = selected semantic_id`
  - or a related-record element if link fields are available in your base
- This pattern is usually the most stable when list-to-list variable filters are not exposed.

Pattern C (fallback): manual semantic_id filter
- Keep Grid 2 as an independent list with `semantic_id contains` filter control.
- Use when your Airtable plan/UI version does not expose `Insert variable` from Grid 1.

Quick troubleshooting when auto-context does not work
- Confirm you are in `Interface` edit mode (not base grid view).
- Confirm both elements are on the same page and not inside incompatible containers.
- Reopen Grid 2 `Data` panel and verify the filter value is a variable token, not typed text.
- Test by clicking 2-3 different Grid 1 rows and watching Grid 2 row count change.
- If no change, switch to Pattern B on the same page.

6) Visual clarity
- Rename sections:
  - `Find an Element (Dictionary)`
  - `Catalog Governance Context`
- Keep row density medium; cap visible fields to reduce clutter.
- Do not nest hierarchy levels on Page A.

7) Save this as your 1.0 page contract
- Page A should answer:
  - `What is this element?`
  - `What’s its governance status?`
  - `What is its FHIR/dictionary curation state?`
  - `Can I move quickly to the canonical catalog record for approval context?`

What not to include on Page A
- HL7 locator search (`PID-5`, `DG1-3`) - put this on Page B (`ddc-hl7_adt_catalog`).
- `upsert_key` column for normal stewards.
- 3-level hierarchy nesting.

2-minute validation checklist
- Can you type `Condition.code` and find it quickly?
- Can you filter readiness fields and narrow quickly?
- When selecting one dictionary row, does Grid 2 update automatically without manual typing?
- Is `semantic_id` always visible?

---

## Page B: HL7 ADT Lookup (PID-5 style search)

Title: `HL7 ADT Lookup`  
Purpose: Find semantic mappings from HL7 locators (`PID-5`, `DG1-3`, `PV1-2`) and review linked context.  
Data source: `ddc-hl7_adt_catalog`.

Build order (fast path)

1) Page shell
- Create/open page `HL7 ADT Lookup`.
- Add text:
  - `Find semantic mapping from HL7 locators like PID-5, DG1-3, PV1-2.`

2) Main ADT list
- Click `Add element` -> `List`.
- Source: `ddc-hl7_adt_catalog`.
- In list settings:
  - Sorts (in order):
    1. `semantic_id` ascending
    2. `message_type` ascending
    3. `segment_id` ascending
    4. `field_id` ascending
  - Show fields:
    - `segment_id`
    - `field_id`
    - `message_type`
    - `semantic_id`
    - `fhir_r4_path`
    - `mapping_status`
    - `Name`
- Keep `upsert_key` hidden on steward view.

3) Add user filters
- Source: `ddc-hl7_adt_catalog` (the main list on Page B).
- Add one fixed filter condition first:
  - `mapping_status` is not `legacy_duplicate`
- Add:
  - `segment_id` equals
  - `message_type` equals/contains
  - Text filter: `field_id` contains (for `PID-5`)
  - Text filter: `semantic_id` contains
  - `mapping_status` equals

4) Add linked catalog detail
- Add detail/list for linked `catalog_element` (catalog row).
- Show:
  - `semantic_id`
  - `uscdi_element`
  - `approval_status`
  - `data_steward`
  - `domain`

5) Add dictionary summary
- Add list/detail from `ddc-master_patient_dictionary`.
- Filter by selected ADT row `semantic_id`.
- Show:
  - `fhir_r4_path`
  - `fhir_data_type`
  - `fhir_profile`
  - `fhir_r4_mapping_readiness`
  - `standards_curation_readiness`

6) Validation
- Can you find `PID-5` via `field_id contains PID-5`?
- Does selecting ADT row show catalog + dictionary context?
- Is `upsert_key` hidden for non-technical users?

---

## Page C: CCDA Lookup (section + XML path)

Title: `CCDA Lookup`  
Purpose: Find semantic mappings from CCDA section, entry type, and XML path.  
Data source: `ddc-ccda_catalog`.

Build order (fast path)

1) Page shell
- Create/open page `CCDA Lookup`.
- Add text:
  - `Find semantic mapping from CCDA section, entry type, and XML path.`

2) Main CCDA list
- Add `List`.
- Source: `ddc-ccda_catalog`.
- In list settings:
  - Sort: `semantic_id`, `section_name`, `entry_type`.
  - Show fields:
    - `section_name`
    - `entry_type`
    - `xml_path`
    - `semantic_id`
    - `fhir_r4_path`
    - `mapping_status`
    - `Name`

3) Add filters
- Source: `ddc-ccda_catalog` (the main list on Page C).
- `section_name` equals
- `entry_type` equals
- Text filter: `xml_path` contains
- Text filter: `semantic_id` contains
- `mapping_status` equals

4) Add linked catalog detail
- Use `catalog_element`.
- Show:
  - `semantic_id`
  - `uscdi_element`
  - `approval_status`
  - `data_steward`

5) Add dictionary summary
- Filter dictionary by selected CCDA row `semantic_id`.
- Show readiness + key FHIR fields.

6) Validation
- Can you locate by XML path fragment?
- Does selected row show catalog + dictionary context?

---

## Page D: Curation Queues (action page)

Title: `Curation Queues`  
Purpose: Triage actionable standards-curation and linkage gaps.  
Data source: `ddc-master_patient_dictionary` (readiness queues) + `ddc-hl7_adt_catalog` (mapping/linkage queues).

Build order (fast path)

1) Page shell
- Create/open page `Curation Queues`.
- Add text:
  - `Actionable queues only. Use this page for triage and follow-up.`

2) Queue 1 - FHIR mapping incomplete
- Add `List`.
- Source: `ddc-master_patient_dictionary`.
- Filter: `fhir_r4_mapping_readiness` is not `Complete`.
- Fields:
  - `semantic_id`
  - `fhir_r4_mapping_readiness`
  - `fhir_r4_mapping_gap_details`
  - `steward_contact`

3) Queue 2 - Standards curation incomplete
- Add `List`.
- Source: `ddc-master_patient_dictionary`.
- Filter: `standards_curation_readiness` is not `Complete`.
- Fields:
  - `semantic_id`
  - `standards_curation_readiness`
  - `standards_curation_gap_details`
  - `steward_contact`

4) Queue 3 - Needs new semantic
- Add `List`.
- Source: `ddc-hl7_adt_catalog`.
- Filter: `mapping_status = needs_new_semantic`.
- Fields:
  - `segment_id`
  - `field_id`
  - `message_type`
  - `semantic_id`
  - `mapping_status`
  - `notes`

5) Queue 4 - Potential unlinked rows
- Add `List`.
- Source: `ddc-hl7_adt_catalog` (optional second block for CCDA).
- Filter: `catalog_element` is empty.
- Fields:
  - `segment_id`
  - `field_id`
  - `semantic_id`
  - `mapping_status`
  - `notes`

6) Optional Queue 5 - Rules needing authoring/review
- Add `List`.
- Source: `ddc-business_rules`.
- Add fixed filters:
  - `active` is `true`
  - `approval_status` is not `approved`
  - `approval_status` is not `deprecated`
- Fields:
  - `semantic_id`
  - `rule_id`
  - `rule_name`
  - `rule_type`
  - `approval_status`
  - `owner`

7) Validation
- Are queues actionable and not noisy?
- Can steward see owner/contact context quickly?

---

## Cross-page behavior (important)

- Airtable pages do not reliably carry selected record context page-to-page.
- Treat each page as independently usable.
- Repeat critical filters on each page.

---

## Optional Omni prompt (sandbox only)

```text
Build a 4-page Airtable Interface for this base:
- Page A Semantic hub: source ddc-master_patient_catalog with filters domain, approval_status, semantic_id contains, uscdi_element contains; show dictionary detail by matching semantic_id.
- Page B HL7 ADT lookup: source ddc-hl7_adt_catalog with filters segment_id, message_type, field_id contains; show linked catalog_element and dictionary summary by semantic_id.
- Page C CCDA lookup: source ddc-ccda_catalog with filters section_name, entry_type, xml_path contains; show linked catalog and dictionary summary.
- Page D Curation queues: dictionary rows where readiness fields are not Complete; ADT rows with mapping_status=needs_new_semantic; rows with empty catalog_element.
Use semantic_id and catalog_element links for relationships. Do not treat Name as join key.
```
