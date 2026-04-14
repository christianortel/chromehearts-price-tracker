from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import PriceObservation, ScrapeRun, Source
from app.services.etl.normalized import NormalizedObservation
from app.services.matching.engine import choose_match, rank_products


def persist_observations(
    db: Session,
    observations: list[NormalizedObservation],
    scrape_run: ScrapeRun | None = None,
) -> list[PriceObservation]:
    persisted: list[PriceObservation] = []

    for normalized in observations:
        source = db.query(Source).filter(Source.name == normalized.source_name).one()
        candidates = rank_products(db, normalized.raw_title)
        chosen = choose_match(candidates)
        observation = PriceObservation(
            product_id=chosen.product_id if chosen else None,
            raw_title=normalized.raw_title,
            normalized_title=normalized.normalized_title,
            source_id=source.id,
            source_item_id=normalized.source_item_id,
            source_url=normalized.source_url,
            source_type_snapshot=normalized.source_type,
            market_side=normalized.market_side,
            seller_or_store=normalized.seller_or_store,
            location_text=normalized.location_text,
            condition=normalized.condition,
            size_text=normalized.size_text,
            currency=normalized.currency,
            price_amount=normalized.price_amount,
            shipping_amount=normalized.shipping_amount,
            tax_included=normalized.tax_included,
            observed_at=normalized.observed_at,
            status="active" if chosen else normalized.status,
            proof_type=normalized.proof_type,
            proof_asset_url=normalized.proof_asset_url,
            extraction_confidence=normalized.extraction_confidence,
            match_confidence=chosen.score if chosen else normalized.match_confidence,
            price_confidence=normalized.price_confidence,
            duplicate_group_key=normalized.duplicate_group_key,
            raw_payload_json=normalized.raw_payload,
        )
        db.add(observation)
        persisted.append(observation)

    db.flush()
    if scrape_run is not None:
        scrape_run.parsed_count += len(observations)
        scrape_run.inserted_count += len(persisted)
    return persisted

