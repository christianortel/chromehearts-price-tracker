from pathlib import Path

from app.core.config import get_settings

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def test_healthcheck(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_products_and_search(client) -> None:
    products = client.get("/products")
    assert products.status_code == 200
    data = products.json()
    assert len(data) >= 100

    search = client.get("/search", params={"q": "Forever Ring"})
    assert search.status_code == 200
    assert search.json()["total"] >= 1


def test_products_support_browse_filters_and_sorting(client) -> None:
    filtered = client.get(
        "/products",
        params=[
            ("q", "CH Forever"),
            ("categories", "ring"),
            ("source_types", "community_retail"),
            ("market_sides", "retail"),
            ("sort", "name_asc"),
        ],
    )
    assert filtered.status_code == 200
    payload = filtered.json()
    assert len(payload) == 1
    assert payload[0]["canonical_name"] == "Chrome Hearts Forever Ring"

    confident = client.get(
        "/products",
        params={
            "source_types": "marketplace",
            "market_sides": "ask",
            "min_confidence": "0.70",
            "sort": "name_asc",
            "limit": 5,
        },
    )
    assert confident.status_code == 200
    confident_payload = confident.json()
    assert confident_payload
    assert confident_payload == sorted(confident_payload, key=lambda item: item["canonical_name"])
    assert all(item["latest_metric"] is not None for item in confident_payload)
    assert all(
        float(item["latest_metric"]["confidence_score"]) >= 0.7 for item in confident_payload
    )


def test_product_browse_metadata_includes_totals_and_facets(client) -> None:
    response = client.get(
        "/products/browse",
        params=[
            ("source_types", "community_retail"),
            ("market_sides", "retail"),
            ("limit", 5),
            ("offset", 0),
        ],
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= len(payload["items"]) >= 1
    assert payload["limit"] == 5
    assert payload["offset"] == 0
    assert payload["has_next_page"] is True
    assert any(
        facet["key"] == "ring" and facet["count"] >= 1 for facet in payload["facets"]["categories"]
    )
    assert any(
        facet["key"] == "community_retail" and facet["count"] >= 1
        for facet in payload["facets"]["source_types"]
    )
    assert any(
        facet["key"] == "retail" and facet["count"] >= 1
        for facet in payload["facets"]["market_sides"]
    )


def test_product_browse_category_facets_ignore_current_category_filter(client) -> None:
    response = client.get(
        "/products/browse",
        params=[
            ("categories", "ring"),
            ("source_types", "community_retail"),
            ("market_sides", "retail"),
        ],
    )
    assert response.status_code == 200
    payload = response.json()
    assert all(item["category"] == "ring" for item in payload["items"])
    category_keys = {facet["key"] for facet in payload["facets"]["categories"]}
    assert "trucker_hat" in category_keys
    assert "ring" in category_keys


def test_admin_unmatched_includes_ranked_candidates(client) -> None:
    response = client.get("/admin/unmatched", headers={"x-admin-token": "change-me"})
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert "top_candidates" in payload[0]
    assert payload[0]["top_candidates"][0]["product_name"]


def test_admin_product_search_supports_alias_lookup(client) -> None:
    response = client.get(
        "/admin/products/search",
        params={"q": "CH Forever"},
        headers={"x-admin-token": "change-me"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "CH Forever"
    assert payload["total"] >= 1
    assert any(item["canonical_name"] == "Chrome Hearts Forever Ring" for item in payload["items"])


def test_admin_alias_create_and_delete(client) -> None:
    create = client.post(
        "/admin/products/1/aliases",
        headers={"x-admin-token": "change-me"},
        json={"alias_text": "Collector Alias", "alias_type": "manual", "source_name": "admin"},
    )
    assert create.status_code == 200
    alias_id = create.json()["id"]

    list_response = client.get("/admin/products/1/aliases", headers={"x-admin-token": "change-me"})
    assert list_response.status_code == 200
    assert any(alias["id"] == alias_id for alias in list_response.json())

    delete = client.delete(f"/admin/aliases/{alias_id}", headers={"x-admin-token": "change-me"})
    assert delete.status_code == 200


def test_admin_source_health_and_scrape_run_flow(client) -> None:
    sources = client.get("/sources")
    assert sources.status_code == 200
    ebay_source = next(source for source in sources.json() if source["name"] == "ebay")

    health = client.get("/admin/source-health", headers={"x-admin-token": "change-me"})
    assert health.status_code == 200
    ebay_health = next(item for item in health.json() if item["source_id"] == ebay_source["id"])
    assert ebay_health["source_type"] == "marketplace"
    assert ebay_health["crawl_method"] == "static_html"
    assert "policy_status" in ebay_health

    disable = client.post(
        f"/admin/sources/{ebay_source['id']}/toggle",
        headers={"x-admin-token": "change-me"},
        json={"enabled": False},
    )
    assert disable.status_code == 200
    assert disable.json()["enabled"] is False

    disabled_run = client.post(
        f"/admin/sources/{ebay_source['id']}/run",
        headers={"x-admin-token": "change-me"},
        json={"query": "chrome hearts"},
    )
    assert disabled_run.status_code == 200
    assert disabled_run.json()["status"] == "disabled"

    enable = client.post(
        f"/admin/sources/{ebay_source['id']}/toggle",
        headers={"x-admin-token": "change-me"},
        json={"enabled": True},
    )
    assert enable.status_code == 200
    assert enable.json()["enabled"] is True

    html = (FIXTURES_DIR / "ebay_search.html").read_text(encoding="utf-8")
    run = client.post(
        f"/admin/sources/{ebay_source['id']}/run",
        headers={"x-admin-token": "change-me"},
        json={"query": "chrome hearts trucker", "html_override": html},
    )
    assert run.status_code == 200
    payload = run.json()
    assert payload["status"] == "success"
    assert payload["source_name"] == "ebay"
    assert payload["discovered_count"] == 1
    assert payload["inserted_count"] == 1

    runs = client.get("/admin/scrape-runs", headers={"x-admin-token": "change-me"})
    assert runs.status_code == 200
    assert any(
        item["id"] == payload["id"] and item["source_name"] == "ebay" for item in runs.json()
    )


def test_admin_scrape_run_detail_includes_persisted_errors(client) -> None:
    sources = client.get("/sources")
    assert sources.status_code == 200
    reddit_source = next(source for source in sources.json() if source["name"] == "reddit")

    if not reddit_source["enabled"]:
        enable = client.post(
            f"/admin/sources/{reddit_source['id']}/toggle",
            headers={"x-admin-token": "change-me"},
            json={"enabled": True},
        )
        assert enable.status_code == 200

    run = client.post(
        f"/admin/sources/{reddit_source['id']}/run",
        headers={"x-admin-token": "change-me"},
        json={"query": "chrome hearts receipts"},
    )
    assert run.status_code == 200
    run_payload = run.json()
    assert run_payload["status"] == "stubbed"
    assert run_payload["error_count"] == 1

    detail = client.get(
        f"/admin/scrape-runs/{run_payload['id']}", headers={"x-admin-token": "change-me"}
    )
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["id"] == run_payload["id"]
    assert detail_payload["source_name"] == "reddit"
    assert len(detail_payload["errors"]) == 1
    assert detail_payload["errors"][0]["error_type"] == "not_implemented"
    assert (
        "disabled pending compliant access approval" in detail_payload["errors"][0]["error_message"]
    )


def test_admin_asset_preview_reads_stored_html_snapshot(client, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ARTIFACT_STORAGE_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        sources = client.get("/sources")
        assert sources.status_code == 200
        ebay_source = next(source for source in sources.json() if source["name"] == "ebay")

        invalid_html = """
        <html>
          <body>
            <ul>
              <li class="s-item">
                <a class="s-item__link" href="https://www.ebay.com/itm/bad-price">
                  <span class="s-item__title">Chrome Hearts Cross Patch Trucker Hat Black</span>
                </a>
                <span class="s-item__price">not-a-price</span>
              </li>
            </ul>
          </body>
        </html>
        """
        run = client.post(
            f"/admin/sources/{ebay_source['id']}/run",
            headers={"x-admin-token": "change-me"},
            json={"query": "chrome hearts trucker", "html_override": invalid_html},
        )
        assert run.status_code == 200
        run_payload = run.json()
        assert run_payload["status"] == "error"
        assert run_payload["error_count"] == 1

        detail = client.get(
            f"/admin/scrape-runs/{run_payload['id']}", headers={"x-admin-token": "change-me"}
        )
        assert detail.status_code == 200
        detail_payload = detail.json()
        snapshot_path = detail_payload["errors"][0]["html_snapshot_path"]
        assert snapshot_path is not None

        preview = client.get(
            "/admin/assets/preview",
            params={"path": snapshot_path},
            headers={"x-admin-token": "change-me"},
        )
        assert preview.status_code == 200
        preview_payload = preview.json()
        assert preview_payload["kind"] == "text"
        assert preview_payload["content_type"] == "text/html"
        assert "not-a-price" in preview_payload["text_content"]
    finally:
        get_settings.cache_clear()


def test_admin_asset_preview_rejects_paths_outside_artifact_root(
    client, monkeypatch, tmp_path
) -> None:
    monkeypatch.setenv("ARTIFACT_STORAGE_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        preview = client.get(
            "/admin/assets/preview",
            params={"path": "../outside.txt"},
            headers={"x-admin-token": "change-me"},
        )
        assert preview.status_code == 400
    finally:
        get_settings.cache_clear()


def test_admin_duplicate_groups_and_review_flow(client) -> None:
    payload = {
        "item_name": "Chrome Hearts Forever Ring",
        "price": "550.00",
        "currency": "USD",
        "store": "Chrome Hearts NYC",
        "city": "New York",
        "country": "US",
        "date_seen": "2026-04-01",
        "notes": "Potential duplicate retail report.",
    }
    created_ids: list[int] = []
    for _ in range(2):
        create = client.post("/submissions", json=payload)
        assert create.status_code == 201
        created_ids.append(create.json()["id"])

    for submission_id in created_ids:
        approve = client.post(
            f"/admin/submissions/{submission_id}/decision",
            params={"decision": "approved", "product_id": 2},
            headers={"x-admin-token": "change-me"},
        )
        assert approve.status_code == 200

    duplicates = client.get("/admin/duplicates", headers={"x-admin-token": "change-me"})
    assert duplicates.status_code == 200
    groups = duplicates.json()
    assert groups
    group = next(
        item
        for item in groups
        if all(
            observation["source_url"].startswith("submission://")
            for observation in item["observations"]
        )
    )
    assert group["duplicate_count"] == 2
    assert group["suggested_keep_observation_id"] in {
        observation["id"] for observation in group["observations"]
    }
    assert group["suggested_keep_reason"]

    reject = client.post(
        "/admin/duplicates/review",
        headers={"x-admin-token": "change-me"},
        json={"observation_id": group["observations"][1]["id"], "decision": "reject"},
    )
    assert reject.status_code == 200

    duplicates_after = client.get("/admin/duplicates", headers={"x-admin-token": "change-me"})
    assert duplicates_after.status_code == 200
    remaining_groups = duplicates_after.json()
    assert not any(
        item["duplicate_group_key"] == group["duplicate_group_key"] for item in remaining_groups
    )


def test_admin_duplicate_group_resolution_keeps_selected_observation(client) -> None:
    payload = {
        "item_name": "Chrome Hearts Forever Ring",
        "price": "550.00",
        "currency": "USD",
        "store": "Chrome Hearts NYC",
        "city": "New York",
        "country": "US",
        "date_seen": "2026-04-02",
        "notes": "Potential duplicate retail report for keeper resolution.",
    }
    created_ids: list[int] = []
    for _ in range(2):
        create = client.post("/submissions", json=payload)
        assert create.status_code == 201
        created_ids.append(create.json()["id"])

    for submission_id in created_ids:
        approve = client.post(
            f"/admin/submissions/{submission_id}/decision",
            params={"decision": "approved", "product_id": 2},
            headers={"x-admin-token": "change-me"},
        )
        assert approve.status_code == 200

    duplicates = client.get("/admin/duplicates", headers={"x-admin-token": "change-me"})
    assert duplicates.status_code == 200
    group = next(
        item
        for item in duplicates.json()
        if all(
            observation["source_url"].startswith("submission://")
            for observation in item["observations"]
        )
    )
    keep_observation_id = group["observations"][0]["id"]

    resolve = client.post(
        "/admin/duplicates/resolve",
        headers={"x-admin-token": "change-me"},
        json={
            "duplicate_group_key": group["duplicate_group_key"],
            "keep_observation_id": keep_observation_id,
        },
    )
    assert resolve.status_code == 200
    resolve_payload = resolve.json()
    assert resolve_payload["keep_observation_id"] == keep_observation_id
    assert len(resolve_payload["rejected_observation_ids"]) == 1

    duplicates_after = client.get("/admin/duplicates", headers={"x-admin-token": "change-me"})
    assert duplicates_after.status_code == 200
    assert not any(
        item["duplicate_group_key"] == group["duplicate_group_key"]
        for item in duplicates_after.json()
    )

    product_observations = client.get("/products/2/observations")
    assert product_observations.status_code == 200
    group_observations = [
        observation
        for observation in product_observations.json()
        if observation["id"] in {item["id"] for item in group["observations"]}
    ]
    kept = next(
        observation
        for observation in group_observations
        if observation["id"] == keep_observation_id
    )
    rejected = next(
        observation
        for observation in group_observations
        if observation["id"] != keep_observation_id
    )
    assert kept["status"] == "active"
    assert rejected["status"] == "rejected"


def test_admin_manual_match_assigns_product(client) -> None:
    unmatched = client.get("/admin/unmatched", headers={"x-admin-token": "change-me"})
    assert unmatched.status_code == 200
    observation = unmatched.json()[0]
    candidate = observation["top_candidates"][0]

    match = client.post(
        "/admin/match",
        headers={"x-admin-token": "change-me"},
        json={
            "observation_id": observation["id"],
            "product_id": candidate["product_id"],
            "decision": "matched",
        },
    )
    assert match.status_code == 200
    assert match.json()["product_id"] == candidate["product_id"]


def test_admin_observation_detail_includes_match_history(client) -> None:
    unmatched = client.get("/admin/unmatched", headers={"x-admin-token": "change-me"})
    assert unmatched.status_code == 200
    observation = unmatched.json()[0]
    candidate = observation["top_candidates"][0]

    match = client.post(
        "/admin/match",
        headers={"x-admin-token": "change-me"},
        json={
            "observation_id": observation["id"],
            "product_id": candidate["product_id"],
            "decision": "matched",
            "reviewer_notes": "Confirmed from admin detail coverage test.",
        },
    )
    assert match.status_code == 200

    detail = client.get(
        f"/admin/observations/{observation['id']}", headers={"x-admin-token": "change-me"}
    )
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["id"] == observation["id"]
    assert payload["source_name"] == observation["source_name"]
    assert payload["product_name"]
    assert payload["top_candidates"]
    assert payload["top_candidates"][0]["product_name"]
    assert isinstance(payload["raw_payload_json"], dict)
    assert payload["match_reviews"]
    assert payload["match_reviews"][0]["reviewer_decision"] == "matched"
    assert payload["match_reviews"][0]["proposed_product_name"]


def test_submissions_and_admin_review_flow(client) -> None:
    create = client.post(
        "/submissions",
        json={
            "item_name": "Chrome Hearts Forever Ring",
            "price": "550.00",
            "currency": "USD",
            "store": "Chrome Hearts NYC",
            "city": "New York",
            "country": "US",
            "date_seen": "2026-04-01",
            "notes": "Receipt-backed.",
            "receipt_asset_url": "https://example.com/receipt.jpg",
        },
    )
    assert create.status_code == 201
    submission_id = create.json()["id"]

    list_response = client.get("/admin/submissions", headers={"x-admin-token": "change-me"})
    assert list_response.status_code == 200
    listed_submission = next(item for item in list_response.json() if item["id"] == submission_id)
    assert listed_submission["top_candidates"]
    assert listed_submission["top_candidates"][0]["product_name"]

    approve = client.post(
        f"/admin/submissions/{submission_id}/decision",
        params={"decision": "approved", "product_id": 2},
        headers={"x-admin-token": "change-me"},
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    observations = client.get("/products/2/observations")
    assert observations.status_code == 200
    submission_observation = next(
        observation
        for observation in observations.json()
        if observation["source_url"] == f"submission://{submission_id}"
    )

    detail = client.get(
        f"/admin/observations/{submission_observation['id']}",
        headers={"x-admin-token": "change-me"},
    )
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["retail_report"] is not None
    assert detail_payload["retail_report"]["moderator_status"] == "approved"
    assert detail_payload["source_name"] == "community_submissions"


def test_submission_asset_upload_and_admin_preview(client, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SUBMISSION_UPLOAD_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        upload = client.post(
            "/submission-assets/upload",
            files={"file": ("receipt.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", "image/jpeg")},
        )
        assert upload.status_code == 201
        upload_payload = upload.json()
        assert upload_payload["asset_path"].startswith("submission-proofs/")
        assert upload_payload["content_type"] == "image/jpeg"

        create = client.post(
            "/submissions",
            json={
                "item_name": "Chrome Hearts Forever Ring",
                "price": "550.00",
                "currency": "USD",
                "store": "Chrome Hearts NYC",
                "city": "New York",
                "country": "US",
                "date_seen": "2026-04-01",
                "notes": "Uploaded proof path.",
                "receipt_asset_url": upload_payload["asset_path"],
            },
        )
        assert create.status_code == 201
        assert create.json()["receipt_asset_url"] == upload_payload["asset_path"]

        submissions = client.get("/admin/submissions", headers={"x-admin-token": "change-me"})
        assert submissions.status_code == 200
        assert any(
            item["receipt_asset_url"] == upload_payload["asset_path"] for item in submissions.json()
        )

        preview = client.get(
            "/admin/assets/preview",
            params={"path": upload_payload["asset_path"]},
            headers={"x-admin-token": "change-me"},
        )
        assert preview.status_code == 200
        preview_payload = preview.json()
        assert preview_payload["kind"] == "image"
        assert preview_payload["content_type"] == "image/jpeg"
        assert preview_payload["base64_content"]
    finally:
        get_settings.cache_clear()


def test_submission_asset_upload_rejects_unsupported_type(client, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SUBMISSION_UPLOAD_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        upload = client.post(
            "/submission-assets/upload",
            files={"file": ("receipt.txt", b"not-supported", "text/plain")},
        )
        assert upload.status_code == 400
    finally:
        get_settings.cache_clear()
