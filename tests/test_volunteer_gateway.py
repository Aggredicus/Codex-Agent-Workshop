"""Static checks for the draft volunteer gateway (browser behavior needs manual tests)."""
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "volunteer" / "index.html"


def _load():
    html = PAGE.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="catalog">\s*(.*?)\s*</script>', html, re.S)
    assert match is not None
    return html, json.loads(match.group(1))


def test_catalog_is_draft_and_consistent():
    _, catalog = _load()
    assert catalog["publication_state"] == "draft"
    assert catalog["opportunities"]
    ids = [o["id"] for o in catalog["opportunities"]]
    assert len(ids) == len(set(ids))
    allowed = {skill["id"] for skill in catalog["skills"]}
    assert allowed
    for opportunity in catalog["opportunities"]:
        assert opportunity["status"] == "candidate"
        assert set(opportunity["skills"]) <= allowed
        assert opportunity["skills"]
        assert opportunity["title"].strip()
        assert opportunity["scope"].strip()
        url = urlparse(opportunity["url"])
        assert url.scheme == "https" and url.netloc == "github.com"
        assert url.path.startswith("/Aggredicus/")


def test_matcher_is_client_only_and_has_accessible_controls():
    html, _ = _load()
    assert 'aria-live="polite"' in html
    assert 'id="skill-grid"' in html
    assert 'type="checkbox"' in html
    assert "localStorage" not in html and "sessionStorage" not in html
    assert "fetch(" not in html and "XMLHttpRequest" not in html
    assert re.search(r'<script\s+src=', html, re.I) is None
    assert "Not yet assigned" in html
    assert "<noscript>" in html
