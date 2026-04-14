# Source Policy Matrix

| Source | Class | Ingestion method | Access status | Official API | Automation needed | Current status | Rate limiting | Fragility risk | Data quality notes | Compliance notes | Kill switch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Legacy CSV importer | community retail / mixed legacy | staged CSV import | available | no | no | implemented | n/a | low | depends on historical sheet hygiene | admin-reviewed before publish | yes |
| eBay | marketplace ask | static HTML search parser | public listings | no stable public API assumed | no for MVP | implemented against parser fixtures, requires live validation | conservative per-source throttle | high | noisy titles, ask != sold, partial attributes | respect robots/compliance review before aggressive backfill | yes |
| Rinkan | curated reseller ask | static HTML parser | public site assumed for listing pages | no confirmed public API | no for MVP | implemented against parser fixtures, requires selector validation | conservative per-source throttle | high | higher signal than marketplaces but still resale asks | monitor terms and disable quickly if site changes | yes |
| Reddit | community retail sightings | adapter interface and normalization pipeline | access depends on API and moderation requirements | limited and policy-sensitive | maybe | stubbed | n/a | medium | community claims may be noisy without receipt proof | do not ingest aggressively without approved access path | yes |
| Justin Reed | curated reseller ask | adapter stub | unknown | unknown | maybe | stubbed | n/a | medium | curated asks can be useful but selector validation pending | manual review before enabling | yes |
| StockX | marketplace / sold signal | adapter stub | uncertain coverage for Chrome Hearts | no confirmed supported official path | maybe | stubbed | n/a | medium | may not cover target catalog well | leave disabled until feasibility confirmed | yes |

