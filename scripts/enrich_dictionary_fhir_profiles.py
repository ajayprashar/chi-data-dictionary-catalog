import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "ddc-master_patient_dictionary.parquet"


def infer_profile(semantic_id: str, fhir_r4_path: str) -> str:
    sid = (semantic_id or "").strip()
    path = (fhir_r4_path or "").strip()
    combo = f"{sid} {path}".lower()

    # Extension-level profiles when explicitly referenced.
    if "us-core-race" in combo:
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
    if "us-core-ethnicity" in combo:
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
    if "us-core-birthsex" in combo:
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex"
    if "us-core-tribal-affiliation" in combo:
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-tribal-affiliation"
    if "patient-religion" in combo:
        return "http://hl7.org/fhir/StructureDefinition/patient-religion"

    # Resource-level defaults (prefer FHIR path over semantic_id prefix).
    if path.startswith("Observation."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-social-history"
    if path.startswith("Encounter."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"
    if path.startswith("Coverage."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-coverage"
    if path.startswith("Condition."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"
    if path.startswith("Patient."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    if sid.startswith("Encounter."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"
    if sid.startswith("Coverage."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-coverage"
    if sid.startswith("Condition."):
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"
    if sid.startswith("Observation.") or sid.startswith("Patient.") or sid.startswith("RelatedPerson."):
        # Fallback to patient when semantic_id namespace is patient-centric but path is ambiguous.
        return "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"

    # No safe inference.
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate missing fhir_profile values in master patient dictionary parquet."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to ddc-master_patient_dictionary.parquet",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output parquet path. If omitted, updates --input in place.",
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Recompute fhir_profile even when current values are non-empty.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    df = pd.read_parquet(input_path)
    if "fhir_profile" not in df.columns:
        raise RuntimeError("Expected column 'fhir_profile' is missing.")
    if "semantic_id" not in df.columns or "fhir_r4_path" not in df.columns:
        raise RuntimeError("Expected columns 'semantic_id' and/or 'fhir_r4_path' are missing.")

    before_non_empty = (df["fhir_profile"].fillna("").astype(str).str.strip() != "").sum()

    def enrich_row(row: pd.Series) -> str:
        current = str(row.get("fhir_profile", "") or "").strip()
        if current and not args.overwrite_existing:
            return current
        return infer_profile(str(row.get("semantic_id", "") or ""), str(row.get("fhir_r4_path", "") or ""))

    df["fhir_profile"] = df.apply(enrich_row, axis=1)
    after_non_empty = (df["fhir_profile"].fillna("").astype(str).str.strip() != "").sum()

    df.to_parquet(output_path, index=False)

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"fhir_profile non-empty before: {before_non_empty}")
    print(f"fhir_profile non-empty after:  {after_non_empty}")


if __name__ == "__main__":
    main()
