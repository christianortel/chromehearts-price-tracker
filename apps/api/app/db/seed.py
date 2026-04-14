from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import PriceObservation, Product, ProductAlias, ProductVariant, RetailReport, Source
from app.services.metrics.engine import recompute_product_metrics
from app.services.normalization import normalize_text


def slugify(value: str) -> str:
    return normalize_text(value).replace(" ", "-")


SOURCE_FIXTURES = [
    {
        "name": "legacy_csv",
        "source_type": "import",
        "base_url": None,
        "crawl_method": "manual_import",
        "policy_status": "implemented",
        "notes": "Historical spreadsheet import staging.",
    },
    {
        "name": "community_submissions",
        "source_type": "community_retail",
        "base_url": None,
        "crawl_method": "manual_entry",
        "policy_status": "implemented",
        "notes": "User-submitted retail sightings with moderation.",
    },
    {
        "name": "ebay",
        "source_type": "marketplace",
        "base_url": "https://www.ebay.com",
        "crawl_method": "static_html",
        "policy_status": "fixture_validated",
        "notes": "Marketplace asking prices from public search results.",
    },
    {
        "name": "rinkan",
        "source_type": "curated_reseller",
        "base_url": "https://rinkan-online.com",
        "crawl_method": "static_html",
        "policy_status": "fixture_validated",
        "notes": "Curated reseller asking prices from listing pages.",
    },
    {
        "name": "reddit",
        "source_type": "community_retail",
        "base_url": "https://www.reddit.com",
        "crawl_method": "api",
        "policy_status": "stubbed",
        "notes": "Stub only until a compliant access path is confirmed.",
    },
    {
        "name": "justin_reed",
        "source_type": "curated_reseller",
        "base_url": "https://www.justinreed.com",
        "crawl_method": "static_html",
        "policy_status": "stubbed",
        "notes": "Source metadata seeded before live parser validation.",
    },
    {
        "name": "stockx",
        "source_type": "sold_comp",
        "base_url": "https://stockx.com",
        "crawl_method": "api",
        "policy_status": "stubbed",
        "notes": "Disabled by default pending feasibility confirmation.",
    },
]


PRODUCT_TEMPLATES = {
    "trucker_hat": {
        "subcategory": "hat",
        "material": "cotton/poly mesh",
        "names": [
            "Cross Patch Trucker Hat Black",
            "Cross Patch Trucker Hat White",
            "Cross Patch Trucker Hat Red",
            "CH Script Trucker Hat Black",
            "Hollywood Trucker Hat Black",
            "Foti Trucker Hat Black",
            "Matty Boy Trucker Hat Orange",
            "Horse Shoe Trucker Hat White",
            "Cemetery Cross Trucker Hat Black",
            "CH Plus Trucker Hat Navy",
            "Cross Patch Trucker Hat Camo",
            "Script Logo Trucker Hat Green",
            "CH Patch Trucker Hat Brown",
            "Double Cross Trucker Hat Black",
            "Fleur Knee Trucker Hat White",
            "CH Stars Trucker Hat Black",
            "Dagger Patch Trucker Hat Black",
            "Matty Boy Warning Trucker Hat Pink",
        ],
    },
    "hoodie": {
        "subcategory": "pullover",
        "material": "cotton fleece",
        "names": [
            "Cross Patch Pullover Hoodie Black",
            "Cross Patch Pullover Hoodie Grey",
            "CH Script Pullover Hoodie Black",
            "Matty Boy Space Pullover Hoodie Black",
            "Matty Boy Brain Pullover Hoodie White",
            "Horse Shoe Pullover Hoodie Black",
            "Cemetery Cross Pullover Hoodie Grey",
            "Dagger Print Pullover Hoodie Black",
            "Foti Pullover Hoodie Black",
            "Neck Logo Pullover Hoodie Heather Grey",
            "Scroll Logo Pullover Hoodie Black",
            "Patchwork Pullover Hoodie Black",
            "Floral Cross Pullover Hoodie White",
            "Vintage Wash Pullover Hoodie Black",
            "Plus Logo Pullover Hoodie Green",
            "Thermal Lined Pullover Hoodie Black",
            "Cross Ball Pullover Hoodie Oatmeal",
            "Hollywood USA Pullover Hoodie Black",
        ],
    },
    "zip_up": {
        "subcategory": "zip hoodie",
        "material": "cotton fleece",
        "names": [
            "Cross Patch Zip Up Hoodie Black",
            "Cross Patch Zip Up Hoodie Grey",
            "CH Script Zip Up Hoodie Black",
            "Matty Boy Zip Up Hoodie Black",
            "Horse Shoe Zip Up Hoodie White",
            "Cemetery Cross Zip Up Hoodie Black",
            "Logo Tape Zip Up Hoodie Black",
            "Dagger Zip Up Hoodie Navy",
            "Foti Zip Up Hoodie Black",
            "Thermal Zip Up Hoodie Black",
            "Scroll Logo Zip Up Hoodie Grey",
            "Plus Print Zip Up Hoodie Green",
            "Cross Ball Zip Up Hoodie Black",
            "Hollywood Zip Up Hoodie Cream",
            "Patch Sleeve Zip Up Hoodie Black",
            "Large CH Patch Zip Up Hoodie Grey",
            "Matty Boy Chomper Zip Up Hoodie Black",
            "Vintage Wash Zip Up Hoodie Charcoal",
        ],
    },
    "long_sleeve": {
        "subcategory": "tee",
        "material": "cotton jersey",
        "names": [
            "Scroll Logo Long Sleeve Tee Black",
            "CH Script Long Sleeve Tee White",
            "Cross Print Long Sleeve Tee Black",
            "Matty Boy Warning Long Sleeve Tee White",
            "Horse Shoe Long Sleeve Tee Black",
            "Dagger Sleeve Long Sleeve Tee Black",
            "Foti Long Sleeve Tee Black",
            "Logo Pocket Long Sleeve Tee White",
            "CH Plus Long Sleeve Tee Grey",
            "Cemetery Cross Long Sleeve Tee Black",
            "Neck Logo Long Sleeve Tee Black",
            "Hollywood USA Long Sleeve Tee White",
            "Thermal Stitch Long Sleeve Tee Black",
            "Floral Sleeve Long Sleeve Tee Black",
            "Cross Ball Long Sleeve Tee White",
            "Vertical Logo Long Sleeve Tee Black",
            "Matty Boy Brain Long Sleeve Tee White",
            "Multi Patch Long Sleeve Tee Black",
        ],
    },
    "ring": {
        "subcategory": "silver ring",
        "material": "sterling silver",
        "names": [
            "Forever Ring",
            "Spacer Ring 6mm",
            "Spacer Ring 3mm",
            "Scroll Band Ring",
            "Cemetery Ring",
            "Cross Band Ring",
            "Dagger Ring",
            "CH Plus Ring",
            "Nail Ring",
            "Tiny E Ring",
            "Floral Ring",
            "Keeper Ring",
            "SBT Band Ring",
            "Cross Tail Ring",
            "Star Band Ring",
            "BS Fleur Ring",
            "Bubblegum Ring",
            "Pyramid Plus Ring",
        ],
    },
    "bracelet": {
        "subcategory": "silver bracelet",
        "material": "sterling silver",
        "names": [
            "Paper Chain Bracelet 7in",
            "Paper Chain Bracelet 8in",
            "Fancy Link Bracelet",
            "Tiny E Bracelet",
            "CH Plus Bracelet",
            "Cross Ball Bracelet",
            "Dagger ID Bracelet",
            "BS Fleur Bracelet",
            "Roll Chain Bracelet",
            "Classic Oval Bracelet",
            "Cemetery Link Bracelet",
            "Filigree Link Bracelet",
            "Safety Pin Bracelet",
            "Double Bangle Bracelet",
            "Spike Link Bracelet",
            "Cross Tail Bracelet",
            "Mini Plus Bracelet",
            "Pyramid Link Bracelet",
        ],
    },
}


def build_seed_products() -> list[dict[str, str | None]]:
    products: list[dict[str, str | None]] = []
    for category, config in PRODUCT_TEMPLATES.items():
        for name in config["names"]:
            products.append(
                {
                    "canonical_name": f"Chrome Hearts {name}",
                    "slug": slugify(f"Chrome Hearts {name}"),
                    "category": category,
                    "subcategory": config["subcategory"],
                    "material": config["material"],
                    "notes": "Seeded starter canonical product for MVP category coverage.",
                }
            )
    return products


def seed_sources(db: Session) -> dict[str, Source]:
    sources: dict[str, Source] = {}
    for payload in SOURCE_FIXTURES:
        existing = db.query(Source).filter(Source.name == payload["name"]).one_or_none()
        if existing is None:
            existing = Source(**payload)
            db.add(existing)
            db.flush()
        sources[existing.name] = existing
    return sources


def seed_products(db: Session) -> list[Product]:
    products: list[Product] = []
    for payload in build_seed_products():
        existing = db.query(Product).filter(Product.slug == payload["slug"]).one_or_none()
        if existing is not None:
            products.append(existing)
            continue
        product = Product(**payload)
        db.add(product)
        db.flush()
        db.add(
            ProductAlias(
                product_id=product.id,
                alias_text=payload["canonical_name"].replace("Chrome Hearts ", "CH "),
                alias_type="abbreviation",
                source_name="seed",
            )
        )
        db.add(
            ProductVariant(
                product_id=product.id,
                size=None,
                color=None,
                finish="default",
                material_detail=payload["material"],
                variant_key=f"{payload['slug']}:default",
            )
        )
        products.append(product)
    return products


def seed_observations(db: Session, products: list[Product], sources: dict[str, Source]) -> None:
    if db.query(PriceObservation).count() > 0:
        return
    sample_products = products[:12]
    for index, product in enumerate(sample_products):
        retail_price = Decimal(425 + (index * 35))
        ask_price = (retail_price * Decimal("1.65")).quantize(Decimal("0.01"))

        retail = PriceObservation(
            product_id=product.id,
            raw_title=product.canonical_name,
            normalized_title=normalize_text(product.canonical_name),
            source_id=sources["community_submissions"].id,
            source_item_id=f"seed-retail-{product.id}",
            source_url=f"seed://retail/{product.id}",
            source_type_snapshot="community_retail",
            market_side="retail",
            seller_or_store="Chrome Hearts Miami",
            location_text="Miami, US",
            currency="USD",
            price_amount=retail_price,
            observed_at=datetime.now(UTC) - timedelta(days=index + 7),
            status="active",
            proof_type="receipt",
            extraction_confidence=Decimal("0.990"),
            match_confidence=Decimal("0.980"),
            price_confidence=Decimal("0.980"),
            raw_payload_json={"seed": True, "market_side": "retail"},
        )
        db.add(retail)
        db.flush()
        db.add(
            RetailReport(
                source_observation_id=retail.id,
                product_id=product.id,
                store_name="Chrome Hearts Miami",
                city="Miami",
                country="US",
                receipt_submitted=True,
                moderator_status="approved",
            )
        )
        db.add(
            PriceObservation(
                product_id=product.id,
                raw_title=product.canonical_name,
                normalized_title=normalize_text(product.canonical_name),
                source_id=sources["ebay"].id,
                source_item_id=f"seed-ask-{product.id}",
                source_url=f"seed://ask/{product.id}",
                source_type_snapshot="marketplace",
                market_side="ask",
                seller_or_store="Sample eBay Seller",
                location_text="US",
                currency="USD",
                price_amount=ask_price,
                shipping_amount=Decimal("20.00"),
                observed_at=datetime.now(UTC) - timedelta(days=index + 2),
                status="active",
                proof_type="listing",
                extraction_confidence=Decimal("0.930"),
                match_confidence=Decimal("0.970"),
                price_confidence=Decimal("0.700"),
                raw_payload_json={"seed": True, "market_side": "ask"},
            )
        )


def seed_all(db: Session) -> None:
    sources = seed_sources(db)
    products = seed_products(db)
    seed_observations(db, products, sources)
    db.flush()
    for product in products[:12]:
        recompute_product_metrics(db, product.id)


def main() -> None:
    with SessionLocal() as db:
        seed_all(db)
        db.commit()


if __name__ == "__main__":
    main()
