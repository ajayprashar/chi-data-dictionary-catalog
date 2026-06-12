"""National standards copy for Guide · National standards PBIP tab.

Keep aligned with docs/shie-standards-reference.md and Notion Authoritative Standards page.
"""

from __future__ import annotations

PAGE_TITLE = "Authoritative standards reference"
PAGE_SUBTITLE = "National and exchange standards cited by CHI metadata - not steward-signed content"
# Header band uses tab label only; subtitle is the first section panel below.

LAYER_LINES = [
    "USCDI = WHAT (Catalog) | US Core on FHIR R4 = HOW (Dictionary) | Terminology = WHICH codes",
    "HL7 v2 ADT + C-CDA R2.1 = WHERE in legacy messages | Crosswalk = local source strings to standards",
    "CHI steward workbook = signed CHI interpretation (approval_status, survivorship, bindings)",
]

EXCHANGE_STANDARDS_LINES = [
    "HL7 FHIR R4 (4.0.1) - structure, cardinality, resource paths (fhir_r4_path). Base: hl7.org/fhir/R4/",
    "US Core - FHIR R4 IG set for Patient demographics and Observations (fhir_profile)",
    "USCDI - v3 = ONC certification baseline (2026); v3.1+ = SVAP / target content",
    "HL7 v2.x ADT - interface profile + MSH-9 message type; segment/field in ADT_Mappings",
    "HL7 C-CDA R2.1 - clinical summary documents; templateId / section / entry in CCDA_Mappings",
]

TERMINOLOGY_LINES = [
    "CDCREC Race / Ethnicity (OID 2.16.840.1.113883.6.238) - Patient.race, Patient.ethnicity",
    "HL7 v3 NullFlavor (OID 2.16.840.1.113883.5.1008) - unknown vs declined vs not asked",
    "BCP 47 (urn:ietf:bcp:47) - primary FHIR binding for Patient.language (RFC 5646 tags)",
    "BCP 47 language subtags often use ISO 639 codes; ISO 639 lists are for legacy intake only",
    "ISO 639 - stewardship / crosswalk: partner or county labels map into BCP 47 for FHIR exchange",
    "LOINC (OID 2.16.840.1.113883.6.1) - e.g. 76691-5 Gender identity for Patient.gender_id",
    "SNOMED CT - coded clinical concepts where US Core bindings apply",
]

SUPPORTING_LINES = [
    "Innovaccer DAP - enterprise terminology at scale (referenced, not duplicated in catalog)",
    "FHIR Provenance (R4) - optional source attribution for conflicting demographics",
    "FIPS county / state codes - geographic identifiers for address and SDOH (not pilot)",
    "Full table + pilot mapping: docs/shie-standards-reference.md",
]
