# Importer

Historical data enters through a staging table, not directly into live observations.

## Flow

1. CSV rows are parsed into `legacy_import_rows`.
2. Duplicates are detected using source identifiers, normalized titles, date windows, and price fingerprints.
3. Default confidence is assigned based on available proof, source provenance, and completeness.
4. Admin reviews rows, maps products, and approves publication.
5. Approved rows are converted into `price_observations` and optional `retail_reports`.

## Implementation

- script entrypoint: `scripts/import_legacy_sheet.py`
- service layer: importer staging and publication helpers
- tests: importer parsing, validation, duplicate detection, and publishing

## Example

```bash
python scripts/import_legacy_sheet.py path/to/legacy.csv
```
