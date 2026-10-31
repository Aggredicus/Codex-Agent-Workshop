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
        r'<script type="application/json" id="offered-catalog">\s*(.*?)\s*</script>',
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


def test_gateway_catalog_script_is_in_sync():
    """The HTML must remain an exact offline projection of canonical JSON."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_gateway_catalogs.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_verified_open_issues_are_explicit_and_not_implied_live():
    html, candidate = _load()
    match = re.search(
        r'<script type="application/json" id="verified-tasks">\s*(.*?)\s*</script>',
        html, re.S
    )
    assert match is not None
    embedded = json.loads(match.group(1))
    canonical = json.loads((ROOT / "docs" / "volunteer" / "open-tasks.json").read_text(encoding="utf-8"))
    assert embedded == canonical
    ids = [t["id"] for t in canonical["tasks"]]
    assert len(ids) == len(set(ids))
    for task in canonical["tasks"]:
        assert task["status_at_verification"] == "open"
        assert task["issue_number"] > 0
        assert task["url"].endswith("/issues/" + str(task["issue_number"]))
        assert set(task["skills"]) <= {s["id"] for s in candidate["skills"]}
    assert "Open at last check" in html
    assert "verify" in canonical["sync_policy"].lower()
    assert "<noscript>" in html


def test_developer_can_syntax_check_inline_javascript(tmp_path):
    """Actual browsers and assistive-technology still need independent tests."""
    import shutil
    import subprocess
    import pytest
    node = shutil.which("node")
    if not node:
        pytest.skip("Node not installed: browser JavaScript syntax unverified")
    html = PAGE.read_text(encoding="utf-8")
    blocks = re.findall(r"<script>\s*(.*?)\s*</script>", html, re.S)
    assert len(blocks) == 1
    file = tmp_path / "gateway.js"
    file.write_text(blocks[0], encoding="utf-8")
    result = subprocess.run([node, "--check", str(file)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_no_duplicate_html_ids_or_untrusted_external_scripts():
    from html.parser import HTMLParser

    class Collector(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = []
            self.external_scripts = []

        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if "id" in values:
                self.ids.append(values["id"])
            if tag == "script" and "src" in values:
                self.external_scripts.append(values["src"])

    collector = Collector()
    collector.feed(PAGE.read_text(encoding="utf-8"))
    assert len(collector.ids) == len(set(collector.ids))
    assert collector.external_scripts == []
