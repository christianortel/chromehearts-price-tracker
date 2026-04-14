# Matching System

The matcher uses three layers.

## Layer 1: deterministic normalization

- lowercase
- punctuation and spacing normalization
- abbreviation expansion
- category and material token extraction
- Chrome Hearts alias normalization

## Layer 2: rules and scoring

- exact alias matches
- near-exact alias matches
- category consistency
- material token agreement
- variant and size compatibility
- source hints and negative keyword penalties

## Layer 3: semantic fallback

When enabled by a configured provider, semantic ranking can break ties for close candidates. The MVP only auto-matches when strict thresholds are met. Ambiguous items remain unmatched for admin review.

## Safety

- rare or vague silver titles do not auto-match aggressively
- low-confidence scores stay out of automatic publication
- admin review and alias editing can override future matches

