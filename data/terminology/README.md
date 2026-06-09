# Terminology expansion cache

Offline fallback for `scripts/build_value_set_members.py`.

After a successful online run:

```powershell
python scripts/build_value_set_members.py --write-cache
```

creates `*.expansion.json` files here (e.g. `v3-Race.expansion.json`). Use `--offline` when `tx.fhir.org` is unavailable.

These files are **reference snapshots**, not CHI governance sign-off. Stewards still approve governed usage via Excel / publish ritual.
