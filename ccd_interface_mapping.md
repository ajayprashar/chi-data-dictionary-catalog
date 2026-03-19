# CCD Interface Mapping (Innovaccer / INV focus)

This document is a **CCD (Continuity of Care Document) interface mapping** oriented toward **Innovaccer (INV)** targets. It maps **source CCD XPaths** to **INV schema** (L2), **INV column**, and **INV display name**. Legacy Syntranet references (DB field, UI field) are omitted so the content stays useful for evaluating how CCD data lands in the same L2/semantic space as the master patient catalog and ADT mappings.

---

## How this helps the chi-data-dictionary-catalog effort

- **Same L2 vocabulary**: INV columns (e.g. `fn`, `ln`, `psa1`, `efdt`, `eid`, `et`, `pd`, `inpid`) align with **data/l2_to_semantic_id_mapping.csv** and CMT ADT. That lets you:
  - Extend **ddc-ccda_catalog.parquet** with more CCD section/XPath → semantic_id rows.
  - Cross-check CCD coverage vs. ADT and master patient elements.
- **CCD section coverage**: The mapping covers Participants (contacts), Encounters, Problems, Medications, Allergies, Immunizations, Results, Vitals, Procedures, Social/Family History, and Insurance. Use it to decide which CCD sections to add to the catalog and to document expected INV (L2) targets.
- **Reference only**: This is reference material. To drive the app or exports, add chosen rows into **ddc-ccda_catalog.parquet** (and optionally the master catalog) via script or manual curation.

---

## Table key

| Column | Meaning |
|--------|--------|
| **CCD section** | High-level CCD section (e.g. Participants, Encounters). |
| **Source CCD XPath** | XPath or path pattern in the source CCD used for this mapping. |
| **INV SCHEMA** | Innovaccer schema (e.g. L2.PD_ACTIVITY). |
| **INV COLUMN** | L2 column name in INV (matches CMT/ADT L2 names where applicable). |
| **INV DISPLAY NAME** | Display name in Innovaccer for this field. |

---

## Participants (contacts / guarantors)

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Participants | associatedEntity/associatedPerson/name/given/node() | Self : L2.PD_ACTIVITY ; Guarantor : L2.PD_ACTIVITY_EXTENSION | Self : fn ; Guarantor : Guarantor_first_name | First Name |
| Participants | associatedEntity/associatedPerson/name/family/node() | L2.PD_ACTIVITY | ln | Last Name |
| Participants | associatedEntity/addr/streetAddressLine[1]/node() | L2.PD_ACTIVITY | psa1 | Patient Primary Street Address 1 |
| Participants | associatedEntity/addr/streetAddressLine[2]/node() | L2.PD_ACTIVITY | psa2 | Patient Primary Street Address 2 |
| Participants | associatedEntity/addr/city/node() | L2.PD_ACTIVITY | pci | Patient Primary City |
| Participants | associatedEntity/addr/state/node() | L2.PD_ACTIVITY | pstn | Patient Primary State Name |
| Participants | associatedEntity/addr/postalCode/node() | L2.PD_ACTIVITY | pz | Patient Primary Zip |
| Participants | associatedEntity/addr/country/node() | L2.PD_ACTIVITY | pcy | Patient Primary Country Code |
| Participants | associatedEntity/telecom/@value | L2.PD_ACTIVITY | tel1 | Patient Primary Telephone |

---

## DocumentationOf (care team / PCP)

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| DocumentationOf | documentationOf/serviceEvent/performer/assignedEntity/id/@extension | L2.PD_ACTIVITY | pcpid | PCP Id |
| DocumentationOf | (performer/assignedEntity) | L2.PD_ACTIVITY | pcpidt | PCP Id Type |

---

## Encounters

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Encounters | {QueryFilter}/effectiveTime | L2.PD_ACTIVITY | efdt | Encounter Start Date |
| Encounters | {code}/code/@code | L2.PD_ACTIVITY | et | Encounter Type |
| Encounters | {id}/id/@extension | L2.PD_ACTIVITY | eid | Encounter ID |
| Encounters | {code}/code/originalText/reference/@value, {Text}/text/reference/@value, {code}/code/@displayName | L2.PD_ACTIVITY | er | Encounter Reason |
| Encounters | {visitprovider}/*/assignedEntity/id/@extension | L2.PD_ACTIVITY | atpnpi | Attending Provider NPI |
| Encounters | (provider type) | L2.PD_ACTIVITY | atpidt | Attending Provider ID Type |
| Encounters | {diagnosisFilter}/value/@code (or translation/@code) | L2.PD_ACTIVITY | pd | Diagnosis code |
| Encounters | {diagnosisFilter}/value/@codeSystem (or translation/@codeSystem) | L2.PD_ACTIVITY | pdcs | Diagnosis Coding System |
| Encounters | {diagnosisFilter}/value/originalText/reference/@value | L2.PD_ACTIVITY | pdn | Diagnosis Name |
| Encounters | {diagnosisFilter}/effectiveTime/high/@value | L2.PD_ACTIVITY | eldt | Encounter End Date |
| Encounters | {serviceEvent}/performer/assignedEntity/code/@displayName | L2.PD_ACTIVITY | sln | Place of Service/Service Location Name |

---

## Problems

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Problems | {ProblemFilter}/code/@code | L2.PD_ACTIVITY | pbc | Problem Code |
| Problems | {ProblemFilter}/entryRelationship[@typeCode='REFR']/observation/value/@code | L2.PD_ACTIVITY | pbst | Problem status (Active, Inactive, Resolved) |
| Problems | {ProblemFilter}/text/reference/@value | L2.PD_ACTIVITY | pbn | Problem Description |
| Problems | {ProblemFilter}/value (code, codeType) | L2.PD_ACTIVITY | pbcs | Problem Coding System |
| Problems | {ProblemFilter}/effectiveTime/low/@value | L2.PD_ACTIVITY | pbfdt | Problem Onset Date |
| Problems | {ProblemFilter}/effectiveTime/high/@value | L2.PD_ACTIVITY | pbldt | Problem Resolution Date |

---

## Medications

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Medications | effectiveTime[@type='IVL_TS'] | L2.PD_ACTIVITY | prdt | Date when medication was prescribed |
| Medications | effectiveTime[@type='EIVL_TS'], doseQuantity | L2.PD_ACTIVITY | rxn | Medication or Substance Name |
| Medications | routeCode[@codeSystem='2.16.840.1.113883.3.26.1.1']/@code | L2.PD_ACTIVITY | mrtcd | Medication Route Code |
| Medications | supply/quantity, dose, doseUnit | L2.PD_ACTIVITY | msrga, rxguc, uqt | Medical dose amount; Dose unit; Unit quantity |
| Medications | entryRelationship/supply/entryRelationship/observation (active) | L2.PD_ACTIVITY | mstn | Medication Status Name |
| Medications | act[templateId/@root='2.16.840.1.113883.10.20.22.4.20']/text/node() | L2.PD_ACTIVITY | prn | Prescription Notes |
| Medications | manufacturedMaterial/code (RXNORM) | L2.PD_ACTIVITY | rxc, rxcs | Medication Code; Medication Coding System |
| Medications | author/assignedAuthor/id[@root='2.16.840.1.113883.4.6']/@extension | L2.PD_ACTIVITY | opn | Ordering Provider Name |

---

## Allergies

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Allergies | {Msg1_Filter}/value/@code | L2.PD_ACTIVITY | alc | Allergen Code |
| Allergies | entryRelationship/observation/value/@code (status) | L2.PD_ACTIVITY | als | Allergy Status |
| Allergies | observation (SEV)/value/@code | L2.PD_ACTIVITY | alsc | Allergy Severity code |
| Allergies | {Msg1_Filter}/effectiveTime/low/@value | L2.PD_ACTIVITY | alrdt | Allergy Record Date |
| Allergies | participant/playingEntity/name | L2.PD_ACTIVITY | aln | Allergen Description |
| Allergies | (alertTypeId, alertStatusId → reaction) | L2.PD_ACTIVITY | alrcn | Allergy Reaction |

---

## Immunizations

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Immunizations | {ImmunizationFilter}/code/@code | L2.PD_ACTIVITY | imc | Immunization Code |
| Immunizations | {ImmunizationFilter}/effectiveTime | L2.PD_ACTIVITY | imfdt | Immunization Start Date |
| Immunizations | {ImmunizationFilter}/effectiveTime | L2.PD_ACTIVITY | imftm | Immunization Start Time |
| Immunizations | performer/assignedEntity/id[@root='2.16.840.1.113883.4.6']/@extension | L2.PD_ACTIVITY | spn | Servicing Provider Name |
| Immunizations | author/assignedAuthor/id[@root='2.16.840.1.113883.4.6']/@extension | L2.PD_ACTIVITY | atpn | Attending Provider Name |
| Immunizations | statusCode/@code | L2.PD_ACTIVITY | ims | Immunization Status |
| Immunizations | consumable/manufacturedProduct/manufacturedMaterial/code/originalText/reference/@value | L2.PD_ACTIVITY | imn | Immunization Name |
| Immunizations | manufacturedMaterial/lotNumberText/node() | L2.PD_ACTIVITY | imsln | Substance Lot Number |
| Immunizations | entryRelationship/observation/value/@value | L2.PD_ACTIVITY | imsn | Immunization Series No |
| Immunizations | consumable/manufacturedProduct/manufacturedMaterial/code | L2.PD_ACTIVITY | (Immunization ID) | Immunization ID |

---

## Results (labs)

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Results | {ResultFilter}/effectiveTime/@value | L2.PD_ACTIVITY | ofdt | Observation Start Date (Collection Date) |
| Results | observation/code[@codeSystem='2.16.840.1.113883.6.1']/@code | L2.PD_ACTIVITY | rc | Lab/Result Code |
| Results | observation/code (codeSystem, nullFlavor) | L2.PD_ACTIVITY | rcs | Result Code System |
| Results | observation/code/@displayName, text/reference/@value | L2.PD_ACTIVITY | rn | Result Test Name |
| Results | observation/text/reference/@value | L2.PD_ACTIVITY | rv | Lab Result Value |
| Results | observation/value/@type | L2.PD_ACTIVITY | obf | Observation Value Format Type |
| Results | referenceRange/observationRange/text/node() | L2.PD_ACTIVITY | onrr | Observation Normal References Range |
| Results | observation/value/@unit | L2.PD_ACTIVITY | sru | Lab Result - Unit |
| Results | referenceRange/value/low/@value, high/@value | L2.PD_ACTIVITY | rrl, rrh | Lab Test Reference Low; Lab Test Reference High |
| Results | (setByNameNPI) | L2.PD_ACTIVITY | opnpi | Ordering Provider NPI |
| Results | {ResultFilter}/code (code, translation) | L2.PD_ACTIVITY | oc, ocs | Order Code; Order Coding System |
| Results | {ResultFilter}/code/@displayName, originalText | L2.PD_ACTIVITY | on | Order Name |
| Results | {ResultFilter}/effectiveTime/@value | L2.PD_ACTIVITY | rdt | Lab Result Date |

---

## Vitals

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Vitals | author/assignedAuthor/id[@root='2.16.840.1.113883.4.6']/@extension | L2.PD_ACTIVITY | atpnpi | Attending Provider NPI |
| Vitals | observation/code/@displayName, originalText, text/reference | L2.PD_ACTIVITY | vn | Vital Name |
| Vitals | observation/effectiveTime/@value | L2.PD_ACTIVITY | vrdt | Vital Record Date |
| Vitals | observation/value/@unit | L2.PD_ACTIVITY | vu | Vital Unit |
| Vitals | observation/value/@value | L2.PD_ACTIVITY | vv | Vital Value |
| Vitals | observation/code/@code | L2.PD_ACTIVITY | vc | Vital Code |

---

## Procedures

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Procedures | {Filter}/text/reference/@value, code/originalText/reference/@value | L2.PD_ACTIVITY | pn | Procedure Name |
| Procedures | {Filter}/code | L2.PD_ACTIVITY | pc | Procedure Code |
| Procedures | {Filter}/effectiveTime/@value | L2.PD_ACTIVITY | pfdt, pftm | Procedure Start Date and time |

---

## Social History

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Social History | {SocialFilter}/text/reference/@value, code/originalText/reference/@value | L2.PD_ACTIVITY | an | Activity Name (e.g. smoking, drinking) |
| Social History | {SocialFilter}/code/@codeSystem, code/translation/@code | L2.PD_ACTIVITY | ac | Activity Code |
| Social History | {SocialFilter}/{codeElementcodeSystem} | L2.PD_ACTIVITY | acs | Activity Coding System |
| Social History | {SocialFilter}/value/@value | L2.PD_ACTIVITY | aov | Activity Observation Value |
| Social History | {SocialFilter}/value/@code | L2.PD_ACTIVITY | aou | Activity Observation Units |
| Social History | {SocialFilter}/statusCode/@code | L2.PD_ACTIVITY | as | Status (Active, Inactive) |
| Social History | {SocialFilter}/effectiveTime/@value | L2.PD_ACTIVITY | ardt | Activity Record date |

---

## Family History

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Family History | component/observation/code/@code, translation/@code | L2.PD_ACTIVITY | fdid, fdnm, fdc | Diagnosis ID; Diagnosis Name; Diagnosis Code |
| Family History | component/observation/code/@codeSystem, translation/@codeSystem | L2.PD_ACTIVITY | fdcs | Diagnosis Coding System |
| Family History | subject/relatedSubject/code[@codeSystem='2.16.840.1.113883.5.111']/@code | L2.PD_ACTIVITY | fdf | Deceased Status |
| Family History | effectiveTime | L2.PD_ACTIVITY | fddt | Diagnosis Date |
| Family History | (relation) | L2.PD_ACTIVITY | frc, frn | Relationship Code; Relationship Name |

---

## Insurance

| CCD section | Source CCD XPath | INV SCHEMA | INV COLUMN | INV DISPLAY NAME |
|-------------|------------------|------------|------------|------------------|
| Insurance | {InsuranceFilter}/act/id/@extension | L2.PD_ACTIVITY | inpid | Insurance Plan ID |
| Insurance | performer/assignedEntity (address) | L2.PD_ACTIVITY | Organization_address1, Organization_city, Organization_state, Organization_zip, Organization_country | Insurance Company Address, City, State, Zip, Country |
| Insurance | assignedEntity (phone, fax, email) | L2.PD_ACTIVITY | organization_phone | Insurance Telephone Number |
| Insurance | act/participant[@typeCode='COV']/time/low/@value | L2.PD_ACTIVITY | inpfdt | Plan Effective Date |
| Insurance | act/participant[@typeCode='COV']/time/high/@value | L2.PD_ACTIVITY | inpldt | Plan Expiration Date |
| Insurance | act/entryRelationship/act/text/reference/@value, getTextContentForID | L2.PD_ACTIVITY | inpn | Insurance Plan Name |
| Insurance | act/participant[@typeCode='COV']/participantRole/id/@extension | L2.PD_ACTIVITY | ptsid | Patient's Subscriber ID |
| Insurance | (patient name from recordTarget) | L2.PD_ACTIVITY | infn, inmn, inln | First/Middle/Last Name of Subscriber |

---

## Summary: INV columns that align with the catalog

Many **INV COLUMN** values match the L2 columns and semantic_ids already in this repo:

- **Demographics / contacts**: fn, ln, psa1, psa2, pci, pstn, pz, pcy, tel1 → same as CMT ADT PID-5, PID-11, PID-13 and master patient (Patient.name_*, Patient.address_*, Patient.phone).
- **Encounters**: efdt, eid, et, er, eldt, sln, atpnpi, atpidt → Encounter.period.start, Encounter.identifier, Encounter.class, Encounter.reasonCode, Encounter.period.end, Encounter.serviceType, Encounter.participant.
- **Diagnosis / problems**: pd, pdcs, pdn, pbc, pbst, pbcs, pbfdt, pbldt → Condition.code and problem list.
- **Insurance**: inpid, inpn, inpfdt, inpldt, ptsid, infn, inmn, inln → Coverage.identifier, plan name, dates, subscriber.
- **PCP / providers**: pcpid, pcpidt → Encounter.participant / PCP.

You can use this mapping to add rows to **ddc-ccda_catalog.parquet** (CCD XPath → semantic_id or INV COLUMN → semantic_id) so the Streamlit app shows CCD mappings alongside ADT for the same elements.
