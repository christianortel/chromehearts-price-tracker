from pathlib import Path

from app.models import LegacyImportRow, PriceObservation, Product, RetailReport
from app.services.etl.importer import publish_staged_row, stage_csv
from sqlalchemy.orm import Session


def test_stage_csv_imports_rows(db_session: Session) -> None:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "legacy_sample.csv"
    count = stage_csv(fixture, db_session)
    assert count == 2
    assert (
        db_session.query(LegacyImportRow)
        .filter(LegacyImportRow.source_name == "legacy_csv")
        .count()
        >= 2
    )


def test_publish_staged_row_creates_observation_and_retail_report(db_session: Session) -> None:
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "legacy_sample.csv"
    stage_csv(fixture, db_session)
    row = (
        db_session.query(LegacyImportRow)
        .filter(LegacyImportRow.external_row_id == "1")
        .order_by(LegacyImportRow.id.desc())
        .first()
    )
    product = db_session.query(Product).filter(Product.category == "ring").first()
    assert row is not None
    assert product is not None
    observation = publish_staged_row(db_session, row, product.id)
    assert db_session.query(PriceObservation).filter(PriceObservation.id == observation.id).one()
    assert (
        db_session.query(RetailReport)
        .filter(RetailReport.source_observation_id == observation.id)
        .one()
    )
