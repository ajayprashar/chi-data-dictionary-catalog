# Presenter script (5 minutes)

One-page script for presenting the **CHI Data Dictionary Catalog** Power BI viewer. Use this for DOPS, steward reviews, or a first walkthrough with program staff.

**Open first:** `workbooks/pbip/chiddc.pbip` (or the extracted release zip). Default landing tab is **Guide · Start here**.

**In-report backup:** The same steps live on **Guide · Walkthrough** if you forget a line.

---

## Before you start (30 seconds)

1. **View -> Zoom -> 100%** and **Actual size** (not Fit to page).
2. Confirm **Home -> Refresh** completed (Report view, not Transform data).
3. Say one sentence up front:

> *This is a read-only **governed catalog viewer** - not a typical analytics dashboard. Stewards edit Excel; everyone else reads here after publish.*

**Do not** open Teams sharing settings, browser tab tricks, or Field guide on a first pass.

---

## The napkin diagram (say once, 20 seconds)

**On screen:** Point at the **layers diagram** on **Guide · Start here** (full color, tab labels). Same asset: `docs/assets/chi_ddc_semantic.png`.

| Layer | Means | Tab |
|-------|--------|-----|
| **WHAT** | USCDI - what CHI governs | Concept Profile (catalog) |
| **HOW** | FHIR R4 / US Core - how we implement | Standards (FHIR row) + Concept Profile (survivorship) |
| **WHICH** | Allowed codes + partner mappings | Standards (two middle tables) |
| **WHERE** | ADT + C-CDA message placement | Standards (bottom tables) |

**Rule of thumb:** **Standards & Contexts** = codes and message placement. **Concept Profile** = steward approval and survivorship.

*(Optional)* On **Standards & Contexts**, the yellow banner repeats the four Ws in one line for drill-down context.

---

## 5-minute script

### Minute 0-1 - Orient

**Tab:** **Guide · Start here** (default) or **Guide · Walkthrough**

**Say:**

> Guide tabs are the built-in user manual. Functional tabs hold the data. For today we use one example: **Patient.race** - one of five Approved demographics pilots.

**Click:** **Standards & Contexts**

---

### Minute 1-2 - Standards and codes

**Slicers:** Set **Demographics pilot only** = `yes`. Set **Concept** = `Patient.race`.

**Say:**

> Everything on this page filters to one patient attribute. The FHIR table shows **how** race is implemented in FHIR R4. The two tables in the middle answer different questions:
>
> - **Left - Governed value set codes:** which standard codes CHI allows (for example CDCREC `2054-5`).
> - **Right - Source value crosswalk:** when a partner sends a local value, which governed code we use.
>
> Crosswalk **target** codes should match the governed list on the left.

**Point only** at ADT/CCDA rows if time allows; do not read column names aloud.

**Skip on first pass:** `code_system_oid`, `hl7_ce_encoding`, null-flavor codes, FHIR extension paths.

---

### Minute 2-3 - Survivorship (plain language)

**Tab:** **Concept Profile** (same concept - `Patient.race`)

**Say:**

> This tab is for **governance and survivorship** - who approved the concept and how we resolve conflicts when sources disagree.
>
> Example: if Michelle has five addresses on file, survivorship rules pick the one we surface on the CHR - usually the most recent address from a trusted source, not an old HMIS-only value.
>
> Empty fields on other concepts are normal - we have only **five** fully curated pilots today.

**Point at:** approval cards and **Implementation & survivorship** table. Do not open Excel or Field guide.

---

### Minute 3-4 - Portfolio status

**Tab:** **Governance Overview**

**Say:**

> Portfolio view: **46** governed concepts, **5** Approved pilots, **41** still need steward review. This is the demographics pilot scope before we scale curation.

**Point at:** KPI cards and approval chart. Scroll the concept table only if asked.

---

### Minute 4-5 - Close with a decision

**Say:**

> **Status:** Excel is the authoring surface; this report is the read surface after import and Refresh. The five-attribute pilot shows we can govern USCDI, FHIR, terminology, crosswalk, and ADT/CCDA in one place - at the cost of real stewardship workflow, not a five-minute spreadsheet.
>
> **Ask:** *For the next step, do you want a deeper standards/engineering session, or governance sign-off on the five pilots?*

Stop. Take questions.

---

## Audience shortcuts

| Audience | Show | Skip |
|----------|------|------|
| Program / Michelle | Slicers, Patient.race, survivorship story, 46/5/41 counts | OID, PID-10.1^10.2, semantic_id |
| Dr. Thomas / DOPS | Pilot status, Excel -> publish ritual, governance gap | Innovaccer DEM, browser tips |
| Developers | Add **Guide · Field guide** after minute 5 | Survivorship analogy (they know it) |

---

## DOPS slot with manifest / Ask Me (10 minutes total)

If the meeting is **not** a full catalog walkthrough:

| Minutes | Topic |
|---------|--------|
| 0-5 | Manifest / Ask Me consent update (what was requested) |
| 5-8 | Optional: **only** Standards & Contexts + Patient.race (Minute 1-2 above) |
| 8-10 | Questions |

Do not merge manifest update and full platform philosophy in one uninterrupted monologue.

---

## Phrases to avoid

- *"Nobody cares except developers"* -> *"Developers use the Field guide for column detail."*
- *"This is overkill"* -> *"This is the level of detail governance requires; the pilot proves the workflow for five attributes."*
- *"Dr. Thomas only wanted a spreadsheet"* -> *"A spreadsheet works for five values; the catalog scales to full stewardship."*

---

## Related docs

- `docs/faq.md` - concept vs element, governed codes vs crosswalk, Standards vs Concept Profile
- `docs/power-bi-concept-profile-setup.md` - open, refresh, troubleshooting
- `docs/operational-runbook.md` - publish ritual (Excel -> import -> Refresh -> git)
- `docs/demographics-pilot-plan.md` - pilot checklist and definition of done
