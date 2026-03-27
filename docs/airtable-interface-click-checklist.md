# Airtable Interface Click Checklist

Use this as the fast, one-pass checklist while you build the live Airtable Interface.

## Before You Start

1. Open `Interfaces` in Airtable, not the base data grid.
2. Confirm these pages exist or create them:
   - `Semantic Hub`
   - `HL7 ADT Lookup`
   - `CCDA Lookup`
   - `Curation Queues`
3. Treat `semantic_id` as the main meaning key.
4. Treat `Name` as display only.
5. Hide `upsert_key` from steward-facing elements.

## Page A: Semantic Hub

1. Add a `List`.
2. Set source to `ddc-master_patient_dictionary`.
3. Title it `Find an Element (Dictionary)`.
4. Sort by `semantic_id` ascending.
5. Show fields:
   - `semantic_id`
   - `fhir_r4_mapping_readiness`
   - `standards_curation_readiness`
   - `fhir_r4_path`
   - `fhir_profile`
6. Add user filters:
   - `fhir_r4_mapping_readiness`
   - `standards_curation_readiness`
   - `semantic_id contains`
   - `fhir_r4_path contains`
7. Turn on row selection / record detail behavior.
8. Add a second element sourced from `ddc-master_patient_catalog`.
9. Filter that second element:
   - field `semantic_id`
   - operator `is` / `equals`
   - value = selected record from the dictionary list -> `semantic_id`
10. Show catalog fields:
   - `semantic_id`
   - `uscdi_element`
   - `uscdi_description`
   - `uscdi_data_class`
   - `uscdi_data_element`
   - `approval_status`
   - `data_steward`
   - `domain`

## Page B: HL7 ADT Lookup

1. Add a `List`.
2. Set source to `ddc-hl7_adt_catalog`.
3. Add a fixed filter:
   - `mapping_status is not legacy_duplicate`
4. Sort by:
   - `semantic_id`
   - `message_type`
   - `segment_id`
   - `field_id`
5. Show fields:
   - `segment_id`
   - `field_id`
   - `message_type`
   - `semantic_id`
   - `fhir_r4_path`
   - `mapping_status`
   - `Name`
6. Add user filters:
   - `segment_id`
   - `message_type`
   - `field_id contains`
   - `semantic_id contains`
   - `mapping_status`
7. Add catalog context using linked field `catalog_element`.
8. Add dictionary summary from `ddc-master_patient_dictionary`.
9. Filter dictionary summary by selected ADT row `semantic_id`.
10. Show dictionary fields:
   - `fhir_r4_path`
   - `fhir_data_type`
   - `fhir_profile`
   - `fhir_r4_mapping_readiness`
   - `standards_curation_readiness`

## Page C: CCDA Lookup

1. Add a `List`.
2. Set source to `ddc-ccda_catalog`.
3. Sort by:
   - `semantic_id`
   - `section_name`
   - `entry_type`
4. Show fields:
   - `section_name`
   - `entry_type`
   - `xml_path`
   - `semantic_id`
   - `fhir_r4_path`
   - `mapping_status`
   - `Name`
5. Add user filters:
   - `section_name`
   - `entry_type`
   - `xml_path contains`
   - `semantic_id contains`
   - `mapping_status`
6. Add catalog detail using `catalog_element`.
7. Add dictionary summary filtered by selected CCDA row `semantic_id`.

## Page D: Curation Queues

1. Add Queue 1 from `ddc-master_patient_dictionary`.
2. Filter Queue 1:
   - `fhir_r4_mapping_readiness is not Complete`
3. Show:
   - `semantic_id`
   - `fhir_r4_mapping_readiness`
   - `fhir_r4_mapping_gap_details`
   - `steward_contact`
4. Add Queue 2 from `ddc-master_patient_dictionary`.
5. Filter Queue 2:
   - `standards_curation_readiness is not Complete`
6. Show:
   - `semantic_id`
   - `standards_curation_readiness`
   - `standards_curation_gap_details`
   - `steward_contact`
7. Add Queue 3 from `ddc-hl7_adt_catalog`.
8. Filter Queue 3:
   - `mapping_status = needs_new_semantic`
9. Show:
   - `segment_id`
   - `field_id`
   - `message_type`
   - `semantic_id`
   - `mapping_status`
   - `notes`
10. Add Queue 4 from `ddc-hl7_adt_catalog`.
11. Filter Queue 4:
   - `catalog_element is empty`
12. Show:
   - `segment_id`
   - `field_id`
   - `semantic_id`
   - `mapping_status`
   - `notes`
13. Add Queue 5 from `ddc-business_rules`.
14. Add fixed filters:
   - `active is true`
   - `approval_status is not approved`
   - `approval_status is not deprecated`
15. Show:
   - `semantic_id`
   - `rule_id`
   - `rule_name`
   - `rule_type`
   - `approval_status`
   - `owner`

## Quick Validation

1. On Page A, click different dictionary rows and confirm the catalog context changes.
2. On Page B, search `PID-5` and confirm only non-legacy ADT rows appear.
3. On Page C, search an XML path fragment and confirm related context appears.
4. On Page D, confirm deprecated business-rule placeholders do not appear.

## Optional UI Cleanup (mark legacy deleted fields)

For each relevant table, confirm these are treated as deleted legacy fields (renamed with `deleted_*` and hidden from views):

- `privacy_security`
- `coverage_personids`
- `granularity_level`
- `business_rule_required`
- `business_rule_notes`

Keep visible:

- `innovaccer_survivorship_logic`
- `reviewer_notes`
