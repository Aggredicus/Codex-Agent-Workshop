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


def test_offered_catalog_matches_offline_embedded_snapshot():
    html, _ = _load()
    match = re.search(
        r'<script type="application/json" id="offered-catalog">\\s*(.*?)\\s*</script>',
        html,
        re.S,
    )
    assert match is not None
    embedded = json.loads(match.group(1))
    canonical = json.loads((ROOT / "docs" / "volunteer" / "offered-skills.json").read_text(encoding="utf-8"))
    assert embedded == canonical
    assert canonical["publication_state"] == "proposed"
    assert canonical["offerings"]
    ids = [o["id"] for o in canonical["offerings"]]
    assert len(ids) == len(set(ids))
    for offer in canonical["offerings"]:
        assert offer["skills"] and offer["sample_deliverables"]
        assert offer["request_scope"] == "public-source"
        url = urlparse(offer["evidence_repository"])
        assert url.scheme == "https"
        assert url.netloc == "github.com"
        assert url.path.startswith("/Aggredicus/")


def test_three_collaboration_paths_and_public_template_links():
    html, _ = _load()
    for anchor in ('id="skills-title"', 'id="request-title"', 'id="trade-title"'):
        assert anchor in html
    for template in ("volunteer-interest.yml", "request-help.yml", "skill-trade.yml"):
        assert (ROOT / ".github" / "ISSUE_TEMPLATE" / template).is_file()
        assert "template=" + template in html
    for form in ("request-help.yml", "skill-trade.yml"):
        contents = (ROOT / ".github" / "ISSUE_TEMPLATE" / form).read_text(encoding="utf-8")
        assert contents.startswith("name:")
        assert "description:" in contents and "body:" in contents
        assert "required: true" in contents
