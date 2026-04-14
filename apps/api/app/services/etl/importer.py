from __future__ import annotations

import csv
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import LegacyImportRow, PriceObservation, RetailReport, Source
from app.services.normalization import build_duplicate_group_key, infer_category, normalize_text


def stage_csv(path: Path, db: Session, source_name: str = "legacy_csv") -> int:
    count = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            raw_item_name = (row.get("item_name") or row.get("item") or "").strip()
            if not raw_item_name:
                continue
            normalized_title = normalize_text(raw_item_name)
            price_amount = Decimal(str(row.get("price") or row.get("amount") or "0"))
            date_hint = row.get("date_seen") or row.get("observed_at") or ""
            duplicate_key = build_duplicate_group_key(
                source_name,
                normalized_title,
                f"{price_amount:.2f}",
                date_hint,
            )
            observed_at = None
            if date_hint:
                try:
                    observed_at = datetime.fromisoformat(date_hint).astimezone(UTC)
                except ValueError:
                    observed_at = None
            staged = LegacyImportRow(
                source_name=source_name,
                external_row_id=row.get("id") or str(index + 1),
                raw_item_name=raw_item_name,
                normalized_title=normalized_title,
                category_hint=infer_category(normalized_title),
                price_amount=price_amount,
                currency=(row.get("currency") or "USD").upper(),
                source_url=row.get("source_url"),
                store=row.get("store"),
                city=row.get("city"),
                country=row.get("country"),
                observed_at=observed_at,
                proof_type=row.get("proof_type"),
                proof_asset_url=row.get("proof_asset_url"),
                duplicate_group_key=duplicate_key,
                raw_payload_json=row,
            )
            db.add(staged)
            count += 1
    db.flush()
    return count


def publish_staged_row(db: Session, row: LegacyImportRow, product_id: int | None) -> PriceObservation:
    source = db.query(Source).filter(Source.name == row.source_name).one()
    observation = PriceObservation(
        product_id=product_id,
        raw_title=row.raw_item_name,
        normalized_title=row.normalized_title,
        source_id=source.id,
        source_item_id=row.external_row_id or str(row.id),
        source_url=row.source_url or "manual://legacy-import",
        source_type_snapshot=source.source_type,
        market_side="retail",
        seller_or_store=row.store,
        location_text=", ".join(filter(None, [row.city, row.country])) or None,
        currency=row.currency,
        price_amount=row.price_amount,
        observed_at=row.observed_at or datetime.now(UTC),
        status="active",
        proof_type=row.proof_type,
        proof_asset_url=row.proof_asset_url,
        extraction_confidence=row.extraction_confidence,
        match_confidence=Decimal("0.800") if product_id else Decimal("0.000"),
        price_confidence=row.price_confidence,
        duplicate_group_key=row.duplicate_group_key,
        raw_payload_json=row.raw_payload_json,
    )
    db.add(observation)
    db.flush()
    db.add(
        RetailReport(
            source_observation_id=observation.id,
            product_id=product_id,
            store_name=row.store,
            city=row.city,
            country=row.country,
            receipt_submitted=(row.proof_type == "receipt"),
            moderator_status="approved",
        )
    )
    row.publish_status = "published"
    return observation

