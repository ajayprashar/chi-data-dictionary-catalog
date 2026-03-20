# Airtable Interface: HIE Data Dictionary & Curation Workspace

This guide aligns with **TECH-SPEC.md** (canonical `semantic_id`, catalog ↔ dictionary 1:1, message catalogs 1:many, **`Name` vs `upsert_key`** in §6.7.1). Use it to build a **reference** Interface stewards and interface engineers can use daily—not only as a one-off AI layout.

---

## Custom Interface vs Airtable Omni AI

| Approach | Best for | Risk |
|----------|----------|------|
| **Custom Interface (recommended baseline)** | Predictable “reference” UX, correct links (`catalog_element`), filters that match your columns, steward training | Upfront design time |
| **Omni AI prompt** | Quick first draft, exploring layouts | Often mis-wires hierarchy, wrong primary field, or 3-level nesting you find confusing; may ignore `semantic_id` vs HL7 rules in §1.8 |
| **Hybrid** | You hand-build **pages + data sources**, then use Omni only for cosmetic tweaks (spacing, copy)—**not** as the source of truth for table links | Medium |

**Recommendation:** Treat **custom Interface** as the **1.0 reference**. Optionally keep a **short Omni “spec prompt”** (appendix below) to regenerate *alternative* drafts in a sandbox Interface, then copy ideas manually into the reference.

---

## Goals the Interface should satisfy

1. **Standards-aligned curation** — Surface USCDI/catalog fields, dictionary FHIR R4 mapping, and QA fields (`fhir_r4_mapping_readiness`, `standards_curation_readiness`, etc.) per TECH-SPEC.
2. **Lookup by concept** — Find an element by `semantic_id`, domain, USCDI label, or readiness.
3. **Lookup by wire format** — Find what a **segment/field** (e.g. `PID-5`, `PV1-2`) maps to; HL7 lives in **`ddc-hl7_adt_catalog`**, not inside `semantic_id` (see TECH-SPEC §1.8: semantic IDs are format-independent).
4. **Stable identity** — Teach users: **`semantic_id`** + links = truth; **`Name`** is display; **`upsert_key`** is technical sync key (ADT/CCDA rows).

---

## Information architecture (suggested pages)

Create **one Interface** with **4 pages** (tabs). Avoid a single 3-level hierarchy unless you truly need drill-down—many teams find **flat list + record detail** clearer.

### Page A — **Semantic hub** (primary)

**Purpose:** “I know the element (or USCDI concept) and want governance + FHIR.”

- **Data source:** `ddc-master_patient_catalog` (or start from `ddc-master_patient_dictionary` if curation columns are the hero—see note below).
- **Layout:**
  - **Top:** Short text / description (static) linking to this doc + TECH-SPEC §1.8.
  - **Filter bar (Interface filters):** e.g. `domain`, `classification`, `approval_status`, `uscdi_data_class` (multi-select where useful).
  - **Main list:** Columns at minimum: `semantic_id`, `uscdi_element`, `approval_status`, `data_steward` (add `uscdi_description` if space).
  - **Record detail (sidebar or full detail):** Linked **`ddc-master_patient_dictionary`** fields via lookup or **linked record** if you model explicit links; if you only have `catalog_element` from catalog side, open dictionary by **filtering a second list** where `semantic_id` matches selected row (see “Synced selection” below).

**Note:** If dictionary holds most QA fields, you can make **dictionary** the primary list and **lookup** catalog columns—but then emphasize `semantic_id` in the list so joins stay obvious.

### Page B — **HL7 ADT lookup** (wire-format search)

**Purpose:** “I have `PID-5` / `DG1-3` / message type **A08**—what is the semantic element?”

- **Data source:** `ddc-hl7_adt_catalog`.
- **Columns:** `segment_id`, `field_id`, `message_type`, `semantic_id`, `fhir_r4_path`, `mapping_status`, `Name` (display), `upsert_key` (optional; hide in steward view, show in “Technical” section).
- **Filters:**
  - **Segment** (`segment_id` = PID, PV1, …)
  - **Field** — use **contains** on `field_id` for values like `PID-5` (your data uses `field_id` such as `PID-5`; free-text “PID#” maps to filtering **PID** + **field**).
- **Detail:** Show linked **catalog** (via `catalog_element`) and a compact **dictionary** summary (FHIR path, readiness) via linked fields or secondary list filtered by `semantic_id`.

### Page C — **CCDA / XML lookup** (optional but parallel to B)

- **Data source:** `ddc-ccda_catalog`.
- **Filters:** `section_name`, `entry_type`; text filter on `xml_path` for path fragments.

### Page D — **Queues & hygiene**

**Purpose:** Steward backlog, not browsing.

- **Lists filtered to:** `fhir_r4_mapping_readiness` ≠ Complete, `standards_curation_readiness` ≠ Complete, `mapping_status` = `needs_new_semantic`, or **empty `catalog_element`** on ADT/CCDA (unlinked queue per TECH-SPEC §1.8.2).

---

## Selection list + “free text” behavior in Interfaces

Airtable Interfaces do **not** replicate a single global “Google-style” search across all tables. Practical patterns:

### 1. **Picker / single select**

- Add a **Filter** element bound to the list: **single select** on `semantic_id` (if cardinality is acceptable) or on `domain` / `classification` first, then narrow.

### 2. **Free text on HL7 “PID#” style**

- **Preferred:** Filter **`field_id`** with condition **contains** `PID-5` (or `5` with segment = PID). Train users: the canonical HL7 locator in data is **`segment_id` + `field_id`**, not `semantic_id`.
- **Optional data improvement:** Add a **formula field** in Airtable (not in Parquet unless you extend the pipeline), e.g. `hl7_locator` = `{segment_id} & "-" & SUBSTITUTE({field_id}, segment & "-", "")` — only if your `field_id` format is consistent. Otherwise filters on `field_id` **contains** are enough.

### 3. **Free text on concept names**

- Use a **Filter** on **`semantic_id`** or **`uscdi_element`** with **contains** (case behavior depends on Airtable field type).
- For richer search across many columns, maintain a **single long text** or **formula** “search blob” field synced from scripts (future enhancement)—Interfaces filter one field reliably.

### 4. **Synced selection across components**

- Use **Interface** patterns that apply **one filter or selected record** to multiple lists (same page): e.g. selecting a catalog row sets a **filter** on child lists (ADT rows where `semantic_id` = selected). Exact mechanics depend on your Airtable plan/UI; if native “sync” is limited, use **Record picker** + **filtered list** linked by `semantic_id`.

---

## Effective list configuration (less confusion than 3-level hierarchy)

Your earlier **3-level** stack (ADT → catalog → dictionary) is **valid** but easy to over-nest.

**Simpler reference pattern:**

1. **One primary list** (catalog *or* dictionary).
2. **Record detail** for the full field set.
3. **Separate linked list** on the same page: “Related ADT mappings” filtered by `semantic_id` = current record (or via `catalog_element` from ADT side).

This preserves **referential clarity** without deep trees.

**When to use 2 levels:** ADT page only—parent list = ADT rows, child = linked catalog row (single expansion).

**When to use 3 levels:** Rare; only if you need ADT → catalog → dictionary **visible at once** without opening record detail.

---

## Field visibility checklist (stewards vs engineers)

| Audience | Emphasize | De-emphasize |
|----------|-----------|----------------|
| **Steward** | `semantic_id`, USCDI, approval, QA readiness, dictionary FHIR columns | `upsert_key`, internal table names |
| **Interface engineer** | ADT `segment_id`, `field_id`, `message_type`, `fhir_r4_path`, `mapping_status` | Long duplicate `Name` if redundant with columns |

---

## Appendix: Short Omni AI spec prompt (optional, sandbox only)

Paste into Omni **only** after you have tables synced; ask it to **not invent fields**. Example:

```text
Build an Airtable Interface for a healthcare data dictionary base with these tables:
- ddc-master_patient_catalog (one row per semantic_id; USCDI and governance)
- ddc-master_patient_dictionary (one row per semantic_id; FHIR R4 mapping and QA fields)
- ddc-hl7_adt_catalog (many rows per semantic_id; HL7 segment_id, field_id, message_type, fhir_r4_path)
Links: catalog_element from child tables to catalog. Do not use Name as join key; use semantic_id and links.

Pages:
1) Semantic hub: catalog list with filters domain, approval_status; record detail shows dictionary fields.
2) HL7 ADT lookup: list from ddc-hl7_adt_catalog with filters on segment_id and field_id contains; show semantic_id and link to catalog.
3) Queues: filtered lists for non-Complete fhir_r4_mapping_readiness.

Avoid 3-level nested hierarchies; use record detail + filtered related lists instead.
```

Review every link and filter Omni creates; **promote to production** only after manual verification.

---

## References

- **TECH-SPEC.md** — §1.8 semantic_id governance, §2.2.1 table names, §6.7.1 `Name` vs `upsert_key`
- **docs/airtable-setup.md** — upload and `catalog_element` population
