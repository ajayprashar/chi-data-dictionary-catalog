# CHI Metadata Catalog — HIE Interoperability Best Practices Evaluation

**Evaluation Date:** March 4, 2026

**Evaluated By:** AI Architecture Review (Claude Sonnet 4.5)

**Scope:** United States Health Information Exchange (HIE) healthcare interoperability best practices

**Implementation Status:** [OK] **Quick Wins Implemented** (see below)

---

## Quick guide for interoperability staff

This document is long and detailed. If you are an interoperability, interface, or program leader and want the **essentials**:

- **What this is**: an independent review of the CHI metadata catalog against common HIE best practices (identity, survivorship, standards, consent, etc.).
- **Key takeaway**: the current POC has a **strong architecture** and is suitable for a demographics‑focused HIE pilot; remaining gaps are mostly normal "POC to production" items.
- **Where to look first**:
  - **Implementation Summary (next section)** — what we changed after the review (new columns, new table, documentation updates).
  - **Executive Summary** — short narrative of strengths, score, and overall assessment.
  - **Priority Gaps for Production HIE** — high‑level list of what would be needed before going live.
- **How to use this**: treat it as a **checklist and reference** when planning a production roadmap; you do not need to read every domain section unless you are designing technical details.

You can stop after these sections if you just need a leadership‑level understanding. The rest of the file is a deep technical dive for architects and engineers.

---

## Implementation Summary (Post-Evaluation)

Following the initial evaluation, the following gaps were addressed through **metadata schema enhancements** suitable for POC scope:

### [OK] Implemented (16 new columns + 1 new table)

**Catalog Additions (10 new columns):**
- `data_steward`, `steward_contact`, `approval_status` — Governance & stewardship assignment
- `schema_version`, `last_modified_date` — Version control & change tracking
- `identifier_type`, `identifier_authority` — Multi-source identity management taxonomy
- `hipaa_category`, `fhir_security_label`, `consent_category` — Enhanced security & consent classification

**Dictionary Additions (8 new columns):**
- `fhir_must_support`, `fhir_profile`, `fhir_cardinality` — FHIR US Core compliance metadata
- `identity_resolution_notes` — Match logic transparency
- `tie_breaker_rule`, `conflict_detection_enabled`, `manual_override_allowed` — Survivorship conflict resolution enhancements
- `de_identification_method` — Privacy & de-identification strategy

**New Table:**
- `data_source_availability.parquet` — Links data sources (feed profiles) to semantic IDs with availability, completeness, and timeliness metadata

**Documentation Updates:**
- Added **Identity Resolution Strategy** section (TECH-SPEC 1.4)
- Added **Security and PHI Handling** section (TECH-SPEC 1.5)
- Updated all schema tables (TECH-SPEC 4.1, 4.2, 4.5)
- Updated UI layout documentation (TECH-SPEC 6.4)
- Updated pipeline summary (TECH-SPEC 7)

### ⏸️ Appropriately Deferred

**Runtime/Operational Concerns (not metadata schema):**
- Field-level provenance tracking (source_system_id + timestamp per actual value)
- Transformation audit trails and ETL logging
- Encryption at rest specifications (deployment concern)
- Actual data quality scoring (requires feed data profiling)

**Beyond POC Scope:**
- Terminology/value set tables (Domain 3: Clinical Governance)
- Clinical data elements (problems, medications, vitals)
- eCQM/HEDIS quality measure linkage
- SDOH screening instrument metadata

**Impact:** POC now addresses **all metadata-related Quick Wins** from EVALUATION.md. Remaining gaps are standard "POC to production" operational concerns or clinical scope expansions.

---

## Executive Summary

### Overall Assessment: **Strong Foundation with Minor Gaps**

Your architecture demonstrates sophisticated understanding of healthcare data interoperability. The implementation of Three-Domain Separation, attribute-specific survivorship, and temporal management for calculated fields is well-aligned with HIE best practices.

**Overall Score: 4.1/5**

---

## Detailed Domain Evaluation

### 1. Patient Identity Management ⭐⭐⭐⭐½

**Strengths:**
- Strong semantic ID strategy with canonical identifiers (`Patient.name_first`, `Patient.birth_date`)
- Explicit privacy/security classification for PII handling
- Recognizes identity attributes as distinct from clinical data (Domain 1 vs Domain 2)

**Gaps:**
- No explicit documentation of **identity resolution strategy** (Verato is mentioned in `hl7_ccd_fhir_consideration.md` but not in core schema)
- Missing **identifier type taxonomy** (MRN, SSN, DL, etc.) in schema
- No **match confidence scoring** or **probabilistic linkage metadata** in dictionary

**Recommendations:**
1. Add `identity_resolution_notes` column to dictionary for match logic transparency
2. Consider adding `identifier_type` and `identifier_authority` to catalog for multi-source identity tracking
3. Document identity merge/unmerge audit trail requirements (not for POC, but for production path)

---

### 2. Master Data Management (MDM) ⭐⭐⭐⭐⭐

**Strengths:**
- Exemplary separation of **catalog** (what exists) vs **dictionary** (how implemented)
- Excellent survivorship architecture with attribute-specific rules
- `data_source_rank_reference` supports flexible hierarchies ("For address: HMIS > Hospital. For legal name: Hospital > HMIS")
- Address coherence via `composite_group` ensures atomic survivorship for related fields

**Gaps:**
- None significant. This is where your architecture excels.

**Best Practice Validation:**
- [OK] Single Best Record (SBR) per attribute
- [OK] Attribute-level survivorship (not entity-level)
- [OK] Source hierarchy transparency
- [OK] Composite attribute coherence

---

### 3. Temporal Data Management (Domain 2) ⭐⭐⭐⭐

**Strengths:**
- Explicit temporal metadata for calculated attributes:
  - `calculation_grain` (monthly/daily/real-time)
  - `historical_freeze` (immutability flag)
  - `recalc_window_months` (rolling window)
- Recognizes difference between **static identity** (Domain 1) and **time-varying calculations** (Domain 2)

**Gaps:**
- No **effective date/end date** tracking in the schema itself (temporal versioning)
- Missing **change data capture (CDC)** metadata for Domain 1 attributes that can change (address moves, name changes)
- No explicit **as-of-date** semantics for survivorship evaluation

**Recommendations:**
1. For production, add `effective_from` and `effective_to` timestamps to dictionary
2. Document **snapshot vs delta** strategy for Domain 1 changes
3. Consider adding `survivorship_evaluation_timestamp` to dictionary for audit trail

**HIE Best Practice Alignment:**
- [OK] Grain-aware calculation (monthly AF/AG housing status)
- [OK] Historical freeze for regulatory compliance
- [WARN] Missing explicit bi-temporal support (transaction time vs valid time)

---

### 4. Standards Alignment ⭐⭐⭐⭐⭐

**Strengths:**
- **FHIR R4** canonical paths for all elements
- **USCDI** anchoring for core data elements
- **HL7 ADT** and **CCDA** message-format catalogs as separate entities
- Clear lineage from L3 master data to multiple output formats

**Best Practice Validation:**
- [OK] Multi-format support (HL7 v2, CCDA, FHIR) without coupling
- [OK] USCDI v4 compliance foundation (extendable to v5/v6)
- [OK] FHIR US Core alignment
- [OK] Separation of structure (catalog) from transformation rules (crosswalk)

**Gap:**
- Missing **value set** and **terminology binding** tables (acknowledged as P2/future)
- No **LOINC/SNOMED/ICD-10** code mappings for clinical governance (Domain 3)

**Recommendation:**
For production HIE, add:
- `terminology_catalog.parquet` (code system, code, display, definition)
- `value_set_bindings.parquet` (semantic_id → required/preferred/example value set)

---

### 5. Roll-Up vs Detail Attributes ⭐⭐⭐⭐⭐

**Strengths:**
- Explicit `rollup_relationship` and `is_rollup` fields
- Supports OMB race/ethnicity rollup requirements
- Enables detailed collection with aggregated reporting

**Best Practice Validation:**
- [OK] Race detailed codes roll up to OMB minimum categories
- [OK] Language detailed codes roll up to preferred language
- [OK] Preserves granularity for partners that can consume detail
- [OK] Provides rollup for partners with simpler requirements

**No gaps.** This is HIE gold standard.

---

### 6. Address Coherence (Composite Attributes) ⭐⭐⭐⭐⭐

**Strengths:**
- `composite_group` ensures street, city, state, zip are survivorship-selected **as a set** from one source at one timestamp
- Prevents "Frankenstein addresses" (street from EHR, zip from HMIS)

**Best Practice Validation:**
- [OK] Atomic survivorship for composite attributes
- [OK] Extensible to other composites (phone + phone type, name + name use)
- [OK] Documented in TECH-SPEC section 1.4

**No gaps.** This is exactly right.

---

### 7. Source Hierarchy and Trust Framework ⭐⭐⭐⭐

**Strengths:**
- `data_source_rank_reference` supports attribute-specific hierarchies
- Recognizes that address recency differs from legal name reliability
- Flexible text format allows complex rules

**Gaps:**
- Text-based source hierarchy is **not machine-readable**
- Missing **feed profile linkage** to catalog (deferred to P2 per TECH-SPEC)
- No **data quality score** or **completeness metric** per source

**Recommendations:**
1. For production, formalize `data_source_rank_reference` as structured JSON or separate table:
   ```json
   {
     "attribute": "Patient.address",
     "hierarchy": ["HMIS", "Hospital_EHR", "Self_Reported"],
     "strategy": "recency",
     "tie_breaker": "source_reliability_score"
   }
   ```
2. Add `data_source_availability.parquet` linking feed profiles to semantic IDs (already identified as P2)
3. Add `source_data_quality_score` (0.0-1.0) to dictionary for completeness/accuracy metrics

---

### 8. Three-Domain Separation ⭐⭐⭐⭐⭐

**Strengths:**
- Explicit `domain` column mapping to:
  - **Domain 1**: Master Demographics (identity, static attributes)
  - **Domain 2**: Master Patient Attributes (calculated, temporal)
  - **Domain 3**: Clinical Governance (terminology, value sets - future)
- Clear governance boundaries
- Different stewardship models accommodated

**Best Practice Validation:**
- [OK] Domain 1 static attributes separate from Domain 2 dynamic calculations
- [OK] Domain 3 clinical governance deferred appropriately for POC
- [OK] Enables different refresh cadences per domain
- [OK] Aligns with National Committee on Vital and Health Statistics (NCVHS) recommendations

**No gaps.** Exemplary architecture.

---

### 9. Message Format Separation ⭐⭐⭐⭐⭐

**Strengths:**
- ADT, CCDA, and master patient catalogs are **siblings, not children**
- Each message format has dedicated catalog with format-specific structure
- 1:many relationship (one semantic_id → many message fields) properly modeled
- Crosswalk strategy prevents coupling L3 truth to format details

**Best Practice Validation:**
- [OK] Format-specific catalogs for structural differences
- [OK] Avoids "one schema to rule them all" anti-pattern
- [OK] Supports multiple partners with different format requirements
- [OK] L3 as canonical truth, messages as renderings

**No gaps.** This is textbook HIE architecture.

---

### 10. Data Quality and Governance ⭐⭐⭐⭐

**Strengths:**
- `data_quality_notes` for steward annotations
- `coverage_personids` for population completeness tracking
- `privacy_security` for PII/sensitive classification
- Multiple survivorship logic fields (HIE vs Innovaccer-specific)

**Gaps:**
- No **data quality dimensions** (completeness, accuracy, timeliness, consistency)
- Missing **stewardship assignment** (who owns each semantic_id)
- No **approval workflow state** (draft/review/approved/deprecated)
- No **version control** for schema changes

**Recommendations:**
1. Add `data_steward` and `approval_status` to catalog
2. Add `schema_version` and `last_modified_date` to both catalog and dictionary
3. For production, implement data quality scoring framework:
   - Completeness: % of patients with non-null values
   - Timeliness: median age of data
   - Consistency: % agreeing across sources

---

### 11. Clinical Data Integration (Domain 3) ⭐⭐⭐

**Strengths:**
- Architecture is **extensible** to clinical data (FHIR paths include Observation, Condition, etc.)
- FHIR resource derivation supports clinical resources
- Strategic deferral of value sets and terminology binding (appropriate for demographics-focused POC)

**Gaps:**
- No **clinical data element** examples yet (problems, medications, vitals, procedures)
- No **LOINC/SNOMED/RxNorm** integration
- No **clinical quality measure (CQM)** linkage
- No **eCQM/HEDIS** metadata

**Status:** Appropriately deferred for POC. For production HIE with clinical data:
1. Add `Observation`, `Condition`, `MedicationStatement` catalog entries
2. Add `terminology_binding` table for required code systems
3. Add `cqm_mapping` for quality measure alignment

---

### 12. Consent and Privacy Framework ⭐⭐⭐

**Strengths:**
- `privacy_security` field for PII/sensitive classification
- Acknowledges ASCMI consent requirements in documentation
- Supports attribute-level privacy (can suppress SSN for specific partners)

**Gaps:**
- No **consent directive modeling** (opt-in/opt-out/break-glass)
- Missing **42 CFR Part 2** (substance use) segment marking
- No **patient consent status** tracking per semantic_id
- Missing **access control metadata** (which roles can view)

**Recommendations:**
1. Add `consent_required` flag to catalog (e.g., "SUD Part 2: requires explicit consent")
2. Add `default_access_level` (public/provider/restricted) to dictionary
3. For production, implement consent policy table linking semantic_id to consent type

---

### 13. Scalability and Extensibility ⭐⭐⭐⭐½

**Strengths:**
- Parquet format for efficient columnar storage
- DuckDB in-memory joins for performance
- Clean separation enables independent scaling of catalog vs dictionary
- Schema upgrade path (`--upgrade-schema`) for backward compatibility

**Gaps:**
- No **partitioning strategy** documented for large-scale deployment
- Missing **caching strategy** for production (Pandas `@lru_cache` won't scale)
- No **incremental update** mechanism (full reload required)

**Recommendations:**
For production HIE scale (millions of patients, hundreds of sources):
1. Partition Parquet files by domain or classification
2. Implement delta lake pattern for incremental updates
3. Add `last_modified_timestamp` for change tracking
4. Consider distributed query engine (Spark, Trino) for analytics workload

---

### 14. Interoperability Crosswalk ⭐⭐⭐⭐

**Strengths:**
- Clear strategy for partner-specific transformation rules
- Unified crosswalk approach prevents rule duplication
- Format-specific catalogs + unified crosswalk is correct pattern

**Gaps:**
- Crosswalk **not yet implemented** (documented as future)
- No **value set mapping** capability
- Missing **conditional logic** for complex transformations

**Recommendation:**
Implement `interoperability_crosswalk.parquet` with:
- Partner ID, format, L3 attribute, target field, transformation rule
- Support for SUPPRESS, MAP_VALUE_SET, ENRICH, VALIDATE operations
- Effective date and version tracking

---

### 15. Feed Profile Integration ⭐⭐⭐⭐

**Strengths:**
- Feed profile CSVs (`*_feed_segments.csv`, `*_feed_event_types.csv`) capture source-specific capabilities
- Separation of **source profile** from **format specification** is correct
- UI displays feed profiles for discoverability

**Gaps:**
- Feed profiles **not linked to catalog semantic IDs** (deferred to P2)
- Missing `data_source_availability` table showing which sources can provide which attributes
- No **source reliability scoring** or **historical performance metrics**

**Recommendation:**
Implement `data_source_availability.parquet`:
- Columns: `source_id`, `semantic_id`, `availability` (full/partial/none), `completeness_pct`, `timeliness_sla_hours`
- Enables intelligent source selection for survivorship

---

### 16. HL7 v2 ADT Support ⭐⭐⭐⭐

**Strengths:**
- Dedicated `hl7_adt_catalog.parquet` for message structure
- Proper 1:many mapping (semantic_id → multiple ADT fields)
- Event type awareness (A01, A03, A08)
- Segment/field/data type/optionality metadata

**Gaps:**
- Only **demographics segments** (PID) in current implementation
- Missing **encounter segments** (PV1, PV2)
- Missing **Z-segment support** for custom extensions
- No **version handling** (HL7 v2.3 vs v2.5.1 differences)

**Status:** Appropriate for POC scope (demographics-focused). For full HIE:
1. Add PV1, PD1, NK1, GT1, IN1 segments
2. Add Z-segment catalog for partner-specific extensions
3. Add `hl7_version` column to support multi-version environments

---

### 17. CCDA/CCD Support ⭐⭐⭐⭐

**Strengths:**
- Dedicated `ccda_catalog.parquet` for XML structure
- Section/entry/xpath mapping
- Proper separation from master patient attributes

**Gaps:**
- Limited to **demographics sections** in POC
- Missing **clinical sections** (Problems, Medications, Results, Vitals)
- No **template ID** tracking (C-CDA R2.1 templates)
- Missing **schematron validation rules**

**Status:** Appropriate for POC. For clinical HIE, extend to full CCDA scope.

---

### 18. FHIR R4 Integration ⭐⭐⭐⭐⭐

**Strengths:**
- Canonical `fhir_r4_path` for every semantic_id
- `fhir_data_type` documentation
- US Core alignment (implicit through USCDI)
- Resource derivation for categorization

**Best Practice Validation:**
- [OK] FHIR as canonical interchange format
- [OK] Supports Patient, Observation, Condition, etc.
- [OK] Structured paths enable automated validation

**Gaps:**
- No **FHIR profile** references (US Core Patient, US Core Race Extension)
- Missing **cardinality constraints** (0..1, 0..*, 1..1)
- No **FHIR search parameter** mapping

**Recommendation:**
Add to dictionary:
- `fhir_profile` (e.g., "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient")
- `fhir_cardinality` (e.g., "0..1", "1..1")
- `fhir_must_support` (boolean) for US Core compliance

---

### 19. Backward Compatibility and Schema Evolution ⭐⭐⭐⭐⭐

**Strengths:**
- Pandas-based data loading with schema tolerance (missing columns backfilled with empty strings)
- `--upgrade-schema` command for in-place Parquet upgrade
- No breaking changes when new HIE columns added

**Best Practice Validation:**
- [OK] Graceful degradation for older data files
- [OK] Zero-downtime schema evolution path
- [OK] Explicit upgrade mechanism

**No gaps.** Excellent production-readiness consideration.

---

### 20. Data Lineage and Provenance ⭐⭐⭐

**Strengths:**
- `data_source_rank_reference` provides source hierarchy transparency
- Feed profiles document source capabilities
- Documentation traces L0-L6 data flow

**Gaps:**
- No **field-level provenance** (which source provided this specific value?)
- Missing **transformation audit trail** (how did raw HL7 PID-5 become Patient.name_first?)
- No **data_source_timestamp** for each attribute value

**Recommendation:**
For production HIE, add provenance tracking:
- `source_system_id` + `source_timestamp` per attribute
- `transformation_log_id` linking to detailed ETL audit table
- `provenance_confidence_score` for derived/calculated fields

---

### 21. Multi-Source Conflict Resolution ⭐⭐⭐⭐

**Strengths:**
- Attribute-specific survivorship logic well-documented
- Recognizes that one-size-fits-all conflict resolution fails
- Address coherence prevents mixed-source contamination

**Gaps:**
- No **tie-breaker rules** when sources have equal rank
- Missing **conflict detection logging** (when sources disagree)
- No **manual override capability** for steward intervention

**Recommendation:**
Add to dictionary:
- `tie_breaker_rule` (e.g., "most_recent", "most_complete", "source_reliability_score")
- `conflict_detection_enabled` (boolean)
- `manual_override_allowed` (boolean) for steward resolution

---

### 22. Security and PHI Handling ⭐⭐⭐

**Strengths:**
- `privacy_security` classification for PII/sensitive
- Attribute-level sensitivity (can tag SSN, HIV status differently than name)

**Gaps:**
- No **encryption at rest** specification
- Missing **de-identification** strategy documentation
- No **minimum necessary** access controls
- Missing **audit logging** requirements

**Recommendations:**
1. Add `hipaa_category` (PII/PHI/SUD_Part2/None) to catalog
2. Add `de_identification_method` (redact/suppress/generalize/pseudonymize) to dictionary
3. Document encryption requirements in TECH-SPEC security section

---

### 23. Race/Ethnicity Interoperability ⭐⭐⭐⭐⭐

**Strengths:**
- Roll-up strategy supports OMB 15 minimum categories + granular capture
- Aligns with USCDI race/ethnicity requirements
- Enables detailed collection with compliant reporting

**Best Practice Validation:**
- [OK] OMB minimum categories (rollup)
- [OK] Detailed race codes (granular)
- [OK] Separate race and ethnicity collection
- [OK] Supports "declined to answer" / "unknown"

**No gaps.** Model solution for race/ethnicity interoperability.

---

### 24. Social Determinants of Health (SDOH) ⭐⭐⭐⭐

**Strengths:**
- SDOH classification explicitly supported
- Housing status (AF/AG) as calculated attribute with temporal grain
- Recognizes SDOH as Domain 2 (calculated) vs Domain 1 (static)

**Best Practice Validation:**
- [OK] USCDI v3+ SDOH requirements
- [OK] Temporal tracking for housing status changes
- [OK] Supports FHIR SDOH Observation profile

**Gap:**
- Missing **SDOH screening instruments** metadata (PRAPARE, AHC-HRSN)
- No **social needs closed loop** tracking (referral → service → outcome)

**Recommendation:**
For full SDOH interoperability, add:
- `screening_instrument` and `loinc_question_code` to dictionary
- Link to care coordination/referral workflows (beyond metadata scope)

---

### 25. Consent and Segmentation ⭐⭐⭐

**Strengths:**
- Acknowledges ASCMI consent requirements
- Privacy classification enables attribute-level segmentation

**Gaps:**
- No **FHIR Consent resource** mapping
- Missing **sensitivity labels** (N/R/V per FHIR security labels)
- No **purpose of use** restrictions (treatment/payment/operations)

**Recommendation:**
Add to catalog:
- `fhir_security_label` (N=normal, R=restricted, V=very restricted)
- `consent_category` (general/research/sensitive)
- Link to FHIR Consent resource for patient opt-in/opt-out

---

## Domain Scoring Summary

| Domain | Score | Status |
|--------|-------|--------|
| Patient Identity Management | 4.5/5 | Strong, minor gaps |
| Master Data Management (MDM) | 5/5 | **Exemplary** |
| Temporal Data Management | 4/5 | Good, missing bi-temporal |
| Standards Alignment | 5/5 | **Exemplary** |
| Roll-Up vs Detail | 5/5 | **Gold Standard** |
| Address Coherence | 5/5 | **Gold Standard** |
| Source Hierarchy | 4/5 | Good, needs machine-readable format |
| Three-Domain Separation | 5/5 | **Exemplary** |
| Message Format Separation | 5/5 | **Textbook HIE** |
| Data Quality/Governance | 4/5 | Good, missing stewardship |
| Clinical Integration (Domain 3) | 3/5 | Appropriately deferred for POC |
| Consent/Privacy Framework | 3/5 | Basic support, needs expansion |
| Lineage/Provenance | 3/5 | Documented but not enforced |
| Multi-Source Conflict Resolution | 4/5 | Good, missing tie-breakers |
| Security/PHI Handling | 3/5 | Classified but not operationalized |
| SDOH Support | 4/5 | Strong for housing, missing screening |

**Overall Average: 4.1/5**

---

## Critical Strengths for HIE

1. **Three-Domain Separation** — Best-in-class governance architecture
2. **Attribute-Specific Survivorship** — Exactly how national HIEs (Carequality, CommonWell) operate
3. **Address Coherence** — Prevents common data quality failure mode
4. **Roll-Up Strategy** — Supports both granular collection and compliant reporting
5. **Message Format Separation** — Avoids coupling that breaks at scale
6. **Backward Compatibility** — Production-grade schema evolution strategy

---

## Priority Gaps for Production HIE

### P1 (Required for Production)
1. **Machine-Readable Source Hierarchy** — Current text format won't scale
2. **Data Source Availability Table** — Links feed profiles to catalog
3. **Provenance Tracking** — Field-level source + timestamp
4. **Stewardship Assignment** — Who owns each semantic_id
5. **Consent Framework** — FHIR Consent resource integration

### P2 (Needed for Clinical HIE)
1. **Terminology/Value Set Tables** — LOINC, SNOMED, RxNorm bindings
2. **Clinical Data Elements** — Extend beyond demographics to problems, meds, vitals
3. **CQM/eCQM Mapping** — Link to quality measures
4. **SDOH Screening Instruments** — PRAPARE, AHC-HRSN

### P3 (Nice to Have)
1. **Data Quality Scoring** — Completeness, timeliness, accuracy metrics
2. **Approval Workflow** — Draft/review/approved state machine
3. **Version Control** — Schema change history

---

## Compliance Assessment

### USCDI v4 (current mandate): ⭐⭐⭐⭐⭐
- Demographics: [OK] Complete
- SDOH: [OK] Housing status supported
- Race/Ethnicity: [OK] OMB + granular
- Sexual Orientation/Gender Identity: [OK] Classified

### USCDI v5 (effective January 2026): ⭐⭐⭐⭐
- Additional SDOH: [WARN] Needs screening instrument metadata
- Care Team: [ERROR] Not yet in scope
- Pediatric Vital Signs: [ERROR] Not yet in scope

### FHIR US Core 6.1.0: ⭐⭐⭐⭐
- Patient resource: [OK] Well-mapped
- Race/Ethnicity extensions: [OK] Supported
- Must Support elements: [WARN] Not explicitly flagged

### Carequality Framework: ⭐⭐⭐⭐
- Trust framework: [OK] Source hierarchy
- Document query: [WARN] CCDA catalog exists but limited
- Patient discovery: [WARN] Identity resolution documented but not schema-enforced

### CommonWell Alliance: ⭐⭐⭐⭐
- Patient matching: [OK] Semantic ID strategy
- Consent directives: [WARN] Acknowledged but not implemented
- Audit logging: [ERROR] Not in metadata scope

---

## Strategic Recommendations

### For Current POC (No Changes Needed)
Your architecture is **excellent for a demographics-focused POC**. The HIE alignment is far beyond typical first attempts. Ship it as-is for stakeholder validation.

### For Production HIE Deployment

**Phase 1: Operationalize Existing Architecture**
- Implement `data_source_availability.parquet`
- Formalize source hierarchy as structured data
- Add provenance tracking (source + timestamp per attribute)
- Implement stewardship assignment

**Phase 2: Expand to Clinical Data**
- Add terminology/value set tables
- Extend catalog to Observation, Condition, Procedure
- Implement clinical quality measure mapping
- Add SDOH screening instrument metadata

**Phase 3: Multi-Partner Interoperability**
- Implement `interoperability_crosswalk.parquet`
- Add partner-specific transformation rules
- Build value set mapping capability
- Implement consent framework

### Quick Wins (High Impact, Low Effort)

1. **Add stewardship columns** to catalog (steward name, contact, approval status)
2. **Add version/date columns** to both catalog and dictionary
3. **Add fhir_must_support** flag to dictionary for US Core compliance
4. **Document identity resolution** strategy in TECH-SPEC
5. **Add tie-breaker rules** to survivorship documentation

---

## Bottom Line

This architecture demonstrates **deep expertise in healthcare data interoperability**. The Three-Domain Separation, attribute-specific survivorship, and message format separation strategies are precisely how mature HIEs (state-level, regional, national networks) operate.

**For a POC:** This is production-grade thinking.  
**For production deployment:** Address P1 gaps (machine-readable source hierarchy, data source availability, provenance, stewardship) before going live.  
**For clinical HIE:** Plan Phase 2 expansion to terminology, value sets, and clinical data elements.

The architecture would score **highly** in any Carequality, CommonWell, or state HIE technical review. The gaps are standard "POC to production" concerns, not fundamental design flaws.

---

## References

- **TECH-SPEC.md** — Section 1.4 HIE Interoperability Alignment
- **hl7_ccd_fhir_consideration.md** — L0-L6 flow and crosswalk strategy
- **USCDI v4** — https://www.healthit.gov/isa/united-states-core-data-interoperability-uscdi
- **FHIR US Core 6.1.0** — http://hl7.org/fhir/us/core/
- **Carequality Interoperability Framework** — https://carequality.org/
- **CommonWell Health Alliance** — https://www.commonwellalliance.org/

---

**Document Version:** 1.0  
**Last Updated:** March 4, 2026
