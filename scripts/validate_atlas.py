#!/usr/bin/env python3
"""Offline safeguards for the Music Archives Italia ten-artist hub."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
ARTISTS = 10

class Hrefs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in ("a", "link", "script"):
            att = dict(attrs)
            ref = att.get("href") or att.get("src")
            if ref:
                self.links.append(ref)

def check_links(page):
    parser = Hrefs()
    parser.feed(page.read_text(encoding="utf-8"))
    missing = []
    for ref in parser.links:
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc or ref.startswith(("#", "mailto:", "tel:")):
            continue
        dest = (page.parent / unquote(parsed.path)).resolve()
        if not dest.is_relative_to(ROOT.resolve()):
            missing.append(f"outside repository: {ref}")
            continue
        if dest.is_dir() or ref.endswith("/"):
            dest /= "index.html"
        if not dest.is_file():
            missing.append(f"missing target {ref}")
    return missing

def main():
    data = json.loads((ROOT / "data/ecosistema-v20.json").read_text(encoding="utf-8"))
    projects = data["projects"]
    assert len(projects) == ARTISTS, "Unexpected artist count"
    assert len({a["portal_directory"] for a in projects}) == ARTISTS, "Duplicate directory"
    assert sum(a["independent_repository"] is not None for a in projects) == 7
    assert all(a["asset_migration_permitted"] is False for a in projects)
    missing = []
    for p in projects:
        if not (ROOT / p["portal_directory"] / "index.html").is_file():
            missing.append(f"missing portal: {p['portal_directory']}")
    for path in ("atlante/index.html", "index.html"):
        missing.extend(f"{path}: {msg}" for msg in check_links(ROOT / path))
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'href="atlante/"' in home, "Homepage has no atlas navigation"
    atlas = (ROOT / "atlante/index.html").read_text(encoding="utf-8")
    assert atlas.count('class="artist-card"') == ARTISTS
    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    for dirname in [p["portal_directory"] for p in projects] + ["atlante", "data"]:
        if f"'{dirname}'" not in workflow and f"'{dirname}/**'" not in workflow:
            missing.append(f"workflow does not include {dirname}")
    if missing:
        raise SystemExit("\n".join(missing))
    print("PASS: ten archive directories, links, manifest, homepage and deploy overlay.")

if __name__ == "__main__":
    main()
