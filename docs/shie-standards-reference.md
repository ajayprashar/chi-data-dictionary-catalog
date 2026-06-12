# SHIE Standards Reference

Governed interoperability and terminology standards used by **SHIE (Community Health Insights)**. Maps each standard to the demographics pilot `semantic_id`s and to steward workbook / dictionary columns.

**Related:** `docs/demographics-pilot-plan.md` (pilot curation), `docs/sources-of-truth.md` (layered authority), `TECH-SPEC.md` (schemas), `ccd_interface_mapping.md` (CCD paths).

**Notion mirror:** [Authoritative Standards / Sources of Truth](https://app.notion.com/p/33c5d66c407f80e59365d15fbb23d639) - keep this doc and that page aligned.

OIDs and canonical URIs belong in the table below where they help implementers. Implementation guides without a single code-system OID use the canonical URL or note that identifiers vary by profile, template, or interface.

---

## How standards layer together

```text
USCDI              →  WHAT elements are in scope (Catalog)
US Core + FHIR R4  →  HOW elements are represented (Dictionary: fhir_r4_path, fhir_profile)
Terminology        →  WHICH coded values are valid (Dictionary: data_quality_notes; Value_Set_*)
HL7 v2 ADT         →  WHERE in legacy ADT feeds (ADT_Mappings)
C-CDA R2.1         →  WHERE in clinical documents (CCDA_Mappings)
Crosswalk          →  Local source strings → standards (Source_Value_Crosswalk)
NullFlavor         →  Non-value states - unknown ≠ declined ≠ missing (survivorship + value sets)
OMB / county       →  Reporting rollups and local→rollup mapping (chi_survivorship_logic)
CHI steward publish →  WHO signed CHI's interpretation (Excel → parquet; not national truth)
```

**OMB** (Office of Management and Budget) defines federal **statistical rollup** categories.  
**CDCREC** (CDC Race & Ethnicity Code Set) is the **terminology authority** for coded race/ethnicity in FHIR/US Core (`ombCategory`, `detailed`). Individual codes use OID `urn:oid:2.16.840.1.113883.6.238` (e.g. race `2054-5` = Black or African American; ethnicity `2135-2` = Hispanic or Latino).

Governance **approval** (`approval_status` = Approved) is steward sign-off on metadata - not the same as terminology code lists.

---

## SHIE standards table

| Standard | Governed version | Code system / OID / canonical URI | Base reference | SHIE use |
|----------|------------------|-----------------------------------|----------------|----------|
| HL7 v2.x ADT | Current operational versions in scope, including v2.3 where required by SHIE interfaces | Interface profile, HL7 version, message type (ADT in MSH-9) - not a single code-system OID | https://hl7-definition.caristix.com/v2/ | Inbound event-based exchange; ADT field mapping (`ADT_Mappings`) |
| HL7 CDA / C-CDA | **C-CDA R2.1** (CDA R2) - current IGs in scope for federal/clinical-summary exchange | Template IDs vary by document/section/entry (`templateId`) | https://www.hl7.org/implement/standards/product_brief.cfm?product_id=492 | Clinical summary documents; CCD paths (`CCDA_Mappings`) |
| HL7 FHIR | **R4 (4.0.1)** | Canonical base: `http://hl7.org/fhir` | https://hl7.org/fhir/R4/ | Primary structure, cardinality, resource mapping (`fhir_r4_path`) |
| USCDI | **v3** = ONC certification baseline (2026); **v3.1+** = SVAP / target content | National data-content baseline - not a terminology code system | https://www.healthit.gov/isa/united-states-core-data-interoperability-uscdi | Catalog identity: `uscdi_element`, `uscdi_description` |
| US Core | FHIR R4-aligned IG set used by SHIE (pin IG version in steward notes when certifying) | `http://hl7.org/fhir/us/core` | https://hl7.org/fhir/us/core/ | `fhir_profile` for Patient demographics extensions and Observations |
| LOINC | Current release in environment | OID: `urn:oid:2.16.840.1.113883.6.1`; canonical: `http://loinc.org` | https://loinc.org/ | Observation codes - e.g. `76691-5` Gender identity for `Patient.gender_id` |
| Innovaccer DAP | Enterprise terminology at scale (referenced) | Platform-managed value sets - not duplicated in CHI catalog | (internal DAP reference) | Cited in dictionary notes; local codes map via crosswalk - not national truth |
| CDCREC Race / HL7 Race Value Set | Current HL7 THO version in environment | OID: `urn:oid:2.16.840.1.113883.6.238` | https://terminology.hl7.org/7.1.0/en/ValueSet-v3-Race.html | `Patient.race` - FHIR `ombCategory` + `detailed` |
| CDCREC Ethnicity / HL7 Ethnicity Value Set | Current HL7 THO version in environment | OID: `urn:oid:2.16.840.1.113883.6.238` | https://terminology.hl7.org/7.1.0/en/ValueSet-v3-Ethnicity.html | `Patient.ethnicity` - FHIR ethnicity extension |
| HL7 v3 NullFlavor | Current HL7 THO version in environment | OID: `urn:oid:2.16.840.1.113883.5.1008`; http://terminology.hl7.org/CodeSystem/v3-NullFlavor | https://terminology.hl7.org/CodeSystem-v3-NullFlavor.html | Unknown, asked-declined, not asked, no information - do not collapse for reporting |
| SNOMED CT | Current release in environment | http://snomed.info/sct; OID: `urn:oid:2.16.840.1.113883.6.96` | https://www.snomed.org/ | Coded clinical concepts; gender identity where applicable |
| HL7 v3 MaritalStatus | Current published reference | http://terminology.hl7.org/CodeSystem/v3-MaritalStatus; OID: `urn:oid:2.16.840.1.113883.5.2` | https://terminology.hl7.org/CodeSystem-v3-MaritalStatus.html | Marital status terminology (not in 5-attribute pilot) |
| BCP 47 Language Tags | Current convention for FHIR bindings | `urn:ietf:bcp:47` | https://www.rfc-editor.org/rfc/rfc5646 | **Primary** FHIR binding for `Patient.language` (RFC 5646 tags; language subtag often from ISO 639) |
| ISO 639 language references | Stewardship / crosswalk only | ISO 639 code lists | https://www.loc.gov/standards/iso639-2/php/code_list.php | Legacy intake and county labels map **into** BCP 47 for exchange - not the FHIR binding OID |
| FHIR Provenance | R4 | http://hl7.org/fhir/StructureDefinition/Provenance | https://hl7.org/fhir/provenance.html | Optional: source attribution for conflicting demographics |
| FIPS County Codes | FIPS 6-4 | ANSI / FIPS county lists | https://www.census.gov/library/reference/code-lists/ansi.html | County ID in address / SDOH (not pilot) |
| FIPS State / ANSI State | FIPS 5-2 / INCITS 38:2009 | ANSI / FIPS state lists | https://www.census.gov/library/reference/code-lists/ansi.html | `Patient.address.state`; postal vs numeric FIPS |

---

## Demographics pilot mapping

| `semantic_id` | USCDI | US Core profile | Terminology authority | NullFlavor / exclusions | County rollup | Message formats |
|---------------|-------|-----------------|----------------------|-------------------------|---------------|-----------------|
| `Patient.race` | Race | `us-core-race` | CDCREC + HL7 Race Value Set; OMB/CDC PHIN for reporting | Unknown, DTS, Other Race excluded from aggregates | Table 5 – Race Groupings; R1–R5, R9, Multi-Racial | ADT PID-10; CCD race |
| `Patient.ethnicity` | Ethnicity | `us-core-ethnicity` | CDCREC + HL7 Ethnicity Value Set | Unknown, declined, patient-refused excluded | Table 5 – Ethnicity; E1/E2 | ADT / CCD ethnicity |
| `Patient.language` | Preferred Language | US Core Patient `communication.language` | **BCP 47** (`urn:ietf:bcp:47`); ISO 639 for crosswalk only | `und`, declined-to-specify excluded | Table 4 – Language Groupings | ADT / CCD language |
| `Patient.gender_id` | Gender Identity | US Core Observation (LOINC 76691-5) | SNOMED / US Core gender identity bindings | Distinct from birth sex / SexID | Table 2 – Gender Groupings (SBR only) | Source-specific |
| `Patient.birth_sex` | Sex | `us-core-birthsex` | Administrative sex codes (not CDCREC) | Unknown (U) treated as null | Table 2 – SexID / SBR rollup | ADT PID-8 etc. |

---

## CDCREC race codes (OMB rollup examples)

Authoritative list: [HL7 Race Value Set](https://terminology.hl7.org/7.1.0/en/ValueSet-v3-Race.html). Common `ombCategory` examples:

| Code | Display (rollup) |
|------|------------------|
| 1002-5 | American Indian or Alaska Native |
| 2028-9 | Asian |
| 2054-5 | Black or African American |
| 2076-8 | Native Hawaiian or Other Pacific Islander |
| 2106-3 | White |
| 2131-1 | Other Race |

`detailed` carries granular codes (e.g. Japanese, Vietnamese) under the rollup. County **Table 5** maps local source values to these groupings.

---

## CDCREC ethnicity codes (examples)

| Code | Display |
|------|---------|
| 2135-2 | Hispanic or Latino |
| 2186-5 | Not Hispanic or Latino |

Detail examples: Mexican, Cuban, Puerto Rican → rollup Hispanic or Latino per county mapping.

---

## Gender identity minimum set (`Patient.gender_id`)

**Observation code (concept):** LOINC `76691-5` - *Gender identity* (`Observation.code`).

**Answer values:** [HL7 Gender Identity ValueSet](http://terminology.hl7.org/ValueSet/gender-identity) - minimum SNOMED set (extensible per US Core). Not interchangeable with `Patient.birth_sex` / CMT `SexID`.

| Code | System | Display | Member role |
|------|--------|---------|-------------|
| 446141000124107 | SNOMED CT | Female gender identity | Standard answer |
| 446151000124109 | SNOMED CT | Male gender identity | Standard answer |
| 33791000087105 | SNOMED CT | Non-binary gender identity | Standard answer |
| UNK | HL7 NullFlavor | Unknown | Non-answer |
| asked-declined | FHIR Data Absent Reason | Asked but declined | Exclude from aggregates |

County **Table 2 – Gender Groupings** applies to SBR / `SexID` rollup only, not this element. Partner-specific identity codes (e.g. Two-Spirit) extend the ValueSet after intake - not in county_master crosswalk today.

**Re-seed members (preserves race/ethnicity expansion):** `python scripts/seed_gender_identity_terminology.py`

---

## NullFlavor (race / ethnicity)

Do not treat these as the same reporting bucket:

| Code | Meaning |
|------|---------|
| UNK | Unknown |
| ASKU | Asked but not known |
| NASK | Not asked |
| NA | Not applicable |
| NI | No information |

County survivorship excludes Unknown / DTS / Other from equity aggregates; FHIR exchange should use governed NullFlavor where source sends non-answers.

---

## Where this lives in the steward workbook

| Standard layer | Sheet | Column(s) |
|----------------|-------|-----------|
| USCDI | Catalog | `uscdi_element`, `uscdi_description`, `classification` |
| US Core / FHIR | Dictionary | `fhir_r4_path`, `fhir_profile`, `fhir_data_type`, `fhir_cardinality` |
| Terminology + NullFlavor | Dictionary | `data_quality_notes` (summary) |
| Governed codes (CHI subset) | **Value_Set_Members** | `ddc-value_set_member.parquet` |
| Value set authority | **Value_Set_Bindings** | `ddc-value_set_binding.parquet` |
| Source → standard map | **Source_Value_Crosswalk** | `ddc-source_value_crosswalk.parquet` |
| County survivorship | Dictionary | `chi_survivorship_logic` |
| HL7 v2 / CCDA paths | ADT_Mappings, CCDA_Mappings | segment/field or XPath → `semantic_id` |
| Re-seed pilot terminology | Script | `python scripts/seed_value_sets_pilot.py` |

Power BI **Standards & Contexts** → **Governed value set codes** and **Source value crosswalk** after publish refresh. See `docs/crosswalk-model.md`.

---

## Re-seed after edits

```powershell
python scripts/seed_demographics_pilot.py
python scripts/generate_steward_workbook.py
```

Then **Refresh** Power BI. Edit `scripts/seed_demographics_pilot.py` if terminology notes change; edit this doc when SHIE adopts new THO/USCDI versions.
