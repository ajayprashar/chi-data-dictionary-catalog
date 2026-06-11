# Partner crosswalk template

**What it is:** A **starter pattern** for documenting how a partner’s **local source codes** map to CHI **governed standard codes** (`ddc-value_set_member`). It is not a full terminology download and not the county survivorship SQL crosswalk (`county_master`).

| Layer | Table | Question it answers |
|-------|--------|-------------------|
| Governed standards | `Value_Set_Members` | What codes are allowed for `Patient.gender_id`? |
| **Partner crosswalk** | `Source_Value_Crosswalk` | What does *our* `GenderIdentity=FEMALE` mean in those standards? |
| County survivorship | `Source_Value_Crosswalk` (`county_master`) | What does the master SQL rollup use? (already seeded) |

Partners **do not** edit the steward workbook. They fill **`Crosswalk_Template`** in `workbooks/chi-partner-intake-workbook.xlsx` (or document codes in **Code_Values** + **Field_Inventory**). CHI stewards copy approved rows into **`Source_Value_Crosswalk`** in `chi-steward-workbook.xlsx`, set the real `source_id`, set `approval_status` = `Approved`, and publish.

---

## Example rows (gender identity)

Template rows use `source_id` = `partner_intake` and `approval_status` = `draft` until a steward signs them.

| Partner `source_field` | Local `source_code` | Maps to (`semantic_id`) | Target | `mapping_type` |
|------------------------|---------------------|---------------------------|--------|----------------|
| GenderIdentity | FEMALE | `Patient.gender_id` | SNOMED 446141000124107 | exact |
| GenderIdentity | MALE | `Patient.gender_id` | SNOMED 446151000124109 | exact |
| GenderIdentity | NONBINARY | `Patient.gender_id` | SNOMED 33791000087105 | exact |
| GenderIdentity | TWO_SPIRIT | `Patient.gender_id` | SNOMED 33791000087105 | rollup |
| GenderIdentity | DECLINE | `Patient.gender_id` | asked-declined | exclude |
| GenderIdentity | UNKNOWN | `Patient.gender_id` | UNK | exclude |

**Common mistake:** mapping **SexID** / **sex at birth** to `Patient.gender_id`. CMT `SexID` and county Table 2 govern **`Patient.birth_sex`** only.

---

## Maintainer: seed template into parquet

```powershell
python scripts/seed_partner_crosswalk_template.py
python scripts/generate_steward_workbook.py
```

Edit mappings in **`data/partner_crosswalk_template.py`**, re-run the seed script, then regenerate the steward workbook. Re-seeding **only replaces** `source_id` = `partner_intake` rows; `county_master` rows are untouched.

---

## Steward workflow after partner intake

1. Review partner **Crosswalk_Template** (and **Code_Values** / **Field_Inventory**).
2. Copy validated rows to steward **`Source_Value_Crosswalk`**.
3. Set `source_id` to the assigned id (e.g. `local_jail`, `cmt`).
4. Set `approval_status` = `Approved` when signed.
5. Publish: `import_steward_workbook_to_parquet.py` → Power BI **Refresh**.

---

## Related

- `docs/crosswalk-model.md` - three-table model
- `docs/shie-standards-reference.md#gender-identity-minimum-set` - governed answer codes
- `docs/excel-workbook-guide.md` - steward vs partner workbooks
