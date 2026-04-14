# Metrics

The metrics pipeline derives product-level snapshots from approved or trusted observations.

## Product metrics

- retail low/high
- best-known retail
- current ask median/low/high
- sold median 30d/90d
- ask and sold sample sizes
- premium percentage and absolute dollars versus best-known retail
- freshness score
- overall confidence score

## Rules

- retail, ask, and sold evidence are computed separately
- stale observations are down-weighted
- premium is omitted when retail evidence is too weak
- low-trust retail signals do not become authoritative best-known retail
- source weighting can raise or lower contribution to final confidence

