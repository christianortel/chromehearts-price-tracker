# Admin Guide

The admin UI is responsible for keeping noisy data honest.

## Core admin flows

- review unmatched observations
- inspect low-confidence matches
- approve or reject user submissions
- manage aliases
- inspect raw payloads and parse failures
- review scrape runs and source health
- recompute metrics after data corrections

## Trust guidelines

- receipt-backed retail submissions can be promoted with high price confidence
- noisy marketplace asks should not be used as retail evidence
- ambiguous silver jewelry titles should remain unmatched until manually reviewed

## Current MVP notes

- unmatched observations now support conservative ranked candidate selection, free-text catalog lookup, and auto-match in the web admin
- submission approval and rejection are wired through the web admin into the backend moderation endpoints, with free-text catalog lookup plus uploaded local proof inspection from admin review cards
- observation detail pages now expose raw payload JSON, proof links, retail-report context, and match-review history for admin inspection
- alias creation and removal are available in `/admin/aliases`
- source operations now support admin-triggered refresh runs, run history inspection, source health visibility, and on/off kill switches from `/admin`
- scrape runs now have dedicated admin detail views that surface persisted scrape errors, HTML snapshot paths, and screenshot paths when available
- stored local scrape artifacts can now be previewed from protected admin pages instead of only displaying raw paths
- duplicate observation groups can now be reviewed from `/admin/duplicates`, including a conservative recommended keeper and a one-click "keep this one" resolution flow
- deeper duplicate merge semantics, richer reviewer notes, and object-storage-backed artifact delivery remain on the backlog
