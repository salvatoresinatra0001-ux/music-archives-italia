#!/usr/bin/env python3
"""Deterministic offline generator for the Music Archives Italia structured catalog."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ("mylene-farmer-italia", "assemblage23-italia", "mesh-italia",
         "sandra-music-italia", "thebirthdaymassacre-italia",
         "ville-valo-him-heartagram-italia")
KINDS = {"album", "ep", "single", "compilation", "live", "remix", "other"}
STATUS = {"verified", "pending"}

def validate(data):
    assert data["schema_version"] == "1.0", "Unsupported schema version"
    artists = data["artists"]
    assert isinstance(artists, list) and len(artists) == 6
    assert {a["id"] for a in artists} == set(SLUGS), "Artist manifest mismatch"
    for artist in artists:
        assert artist["path"] == artist["id"]
        assert artist["name"].strip()
        assert isinstance(artist["release_records"], list)
        assert isinstance(artist["source_records"], list)
        sources = set()
        for source in artist["source_records"]:
            assert source["id"] not in sources
            sources.add(source["id"])
            assert source["title"].strip() and source["url"].startswith("https://")
        seen = set()
        for release in artist["release_records"]:
            assert release["id"] not in seen, "Duplicate release identifier"
            seen.add(release["id"])
            assert release["title"].strip()
            assert release["kind"] in KINDS
            assert release["verification"] in STATUS
            assert isinstance(release["year"], int) and 1900 <= release["year"] <= 2100
            assert isinstance(release["source_ids"], list)
            assert set(release["source_ids"]) <= sources, "Unknown source identifier"
            if release["verification"] == "verified":
                assert release["source_ids"], "Verified releases require citations"
    return artists

def page(artist):
    name = html.escape(artist["name"])
    rows = []
    for r in sorted(artist["release_records"], key=lambda r: (r["year"], r["title"].casefold())):
        title = html.escape(r["title"])
        kind = html.escape(r["kind"])
        label = "Documentato" if r["verification"] == "verified" else "Da verificare"
        rows.append(f"<tr><td>{r['year']}</td><td>{title}</td><td>{kind}</td><td>{label}</td></tr>")
    table = ("<table><thead><tr><th>Anno</th><th>Titolo</th><th>Tipo</th><th>Stato</th></tr></thead><tbody>" +
             "".join(rows) + "</tbody></table>") if rows else (
             "<p>Catalogo strutturato in preparazione. Nessuna edizione è stata ancora "
             "inserita come scheda documentata: consulta la discografia editoriale esistente.</p>")
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Catalogo strutturato di {name}, archivio indipendente.">
<title>Catalogo strutturato | {name}</title>
<link rel="stylesheet" href="../assets/editorial.css"></head>
<body><header class="top"><div class="wrap nav"><a class="brand" href="../index.html">MUSIC ARCHIVES ITALIA</a>
<nav class="links"><a href="./">Home</a><a href="discografia.html">Discografia</a>
<a href="singoli.html">Brani</a><a href="collaborazioni.html">Collaborazioni</a>
<a href="ricerca.html">Fonti</a></nav></div></header>
<main id="contenuto"><section class="hero"><div class="wrap"><p class="eyebrow">Archivio dati / v3.0</p>
<h1>Catalogo strutturato</h1><p class="lead">{name}</p></div></section>
<section class="section"><div class="wrap content"><h2>Pubblicazioni indicizzate</h2>{table}
<p class="note">Le schede documentate richiedono almeno una fonte identificabile.
La pagina distingue le informazioni verificate dalle registrazioni in attesa di controllo.
Non rappresenta una discografia completa.</p>
<a class="cta" href="discografia.html">Discografia editoriale →</a>
<a class="cta" href="ricerca.html">Metodo e fonti →</a></div></section></main>
<footer class="footer"><div class="wrap">© 2026 Salvatore Sinatra · Archivio indipendente non ufficiale.</div></footer></body></html>"""


def get_attr(tag, name):
    import re
    pattern = r"""(?:^|\s)""" + re.escape(name) + r"""\s*=\s*(["'])(.*?)\1"""
    match = re.search(pattern, tag, re.I | re.S)
    return html.unescape(match.group(2)) if match else None


def insert_head_content(document, snippet):
    """Insert metadata inside the existing head; never prepend pseudo-heads."""
    import re
    closing = re.search(r"</head\s*>", document, re.I)
    if closing:
        return document[:closing.start()] + snippet + "\n" + document[closing.start():]
    body = re.search(r"<body\b", document, re.I)
    if body:
        return document[:body.start()] + "<head>\n" + snippet + "\n</head>\n" + document[body.start():]
    root = re.search(r"<html\b[^>]*>", document, re.I)
    if root:
        return document[:root.end()] + "\n<head>\n" + snippet + "\n</head>\n" + document[root.end():]
    raise ValueError("Cannot insert metadata: document has no HTML root or body")


def set_meta(document, attribute, key, value):
    import re
    pattern = re.compile(r"<meta\b[^>]*>", re.I)
    escaped = html.escape(value, quote=True)
    matches = [
        match for match in pattern.finditer(document)
        if (get_attr(match.group(0), attribute) or "").casefold() == key.casefold()
    ]
    if not matches:
        tag = f'<meta {attribute}="{html.escape(key, quote=True)}" content="{escaped}">'
        return insert_head_content(document, tag)

    first = matches[0]
    tag = first.group(0)
    content_pattern = re.compile(r"""(\scontent\s*=\s*)(["'])(.*?)\2""", re.I | re.S)
    if content_pattern.search(tag):
        edited_tag = content_pattern.sub(
            lambda match: match.group(1) + match.group(2) + escaped + match.group(2),
            tag,
            count=1,
        )
    else:
        edited_tag = re.sub(r"\s*/?>$", ' content="' + escaped + '">', tag)
    document = document[:first.start()] + edited_tag + document[first.end():]

    # Deduplicate pre-existing repeated metadata without disturbing markup.
    duplicates = [
        match for match in pattern.finditer(document)
        if (get_attr(match.group(0), attribute) or "").casefold() == key.casefold()
    ]
    for extra in reversed(duplicates[1:]):
        document = document[:extra.start()] + document[extra.end():]
    return document


def page_url_for(page_path, output, base):
    relative = page_path.relative_to(output).as_posix()
    if relative == "index.html":
        return base
    if relative.endswith("/index.html"):
        return base + quote(relative[:-len("/index.html")], safe="/-._~") + "/"
    return base + quote(relative, safe="/-._~")


def ensure_page_seo(page_path, output, base):
    import re
    document = page_path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", document, re.I | re.S)
    title = (
        html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip())
        if title_match
        else page_path.stem.replace("-", " ").title() + " — Music Archives Italia"
    )

    description = None
    for meta in re.findall(r"<meta\b[^>]*>", document, re.I):
        if (get_attr(meta, "name") or "").casefold() == "description":
            description = get_attr(meta, "content")
            break
    if not description:
        h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", document, re.I | re.S)
        excerpt = html.unescape(re.sub(r"<[^>]+>", " ", h1.group(1))).strip() if h1 else title
        description = (excerpt + " — Archivio musicale indipendente in lingua italiana a cura di Salvatore Sinatra.")[:175]
        document = set_meta(document, "name", "description", description)

    canonical = None
    for link in re.findall(r"<link\b[^>]*>", document, re.I):
        if "canonical" in ((get_attr(link, "rel") or "").lower().split()):
            canonical = get_attr(link, "href")
            if canonical:
                break
    if not canonical:
        canonical = page_url_for(page_path, output, base)
        document = insert_head_content(
            document,
            '<link rel="canonical" href="' + html.escape(canonical, quote=True) + '">',
        )

    for key, value in (
        ("og:type", "website"),
        ("og:locale", "it_IT"),
        ("og:site_name", "Music Archives Italia"),
        ("og:title", title),
        ("og:description", description),
        ("og:url", canonical),
    ):
        document = set_meta(document, "property", key, value)

    image = None
    for meta in re.findall(r"<meta\b[^>]*>", document, re.I):
        if (get_attr(meta, "property") or "").casefold() == "og:image":
            image = get_attr(meta, "content")
            break

    document = set_meta(document, "name", "twitter:card", "summary_large_image" if image else "summary")
    document = set_meta(document, "name", "twitter:title", title)
    document = set_meta(document, "name", "twitter:description", description)
    if image:
        document = set_meta(document, "name", "twitter:image", image)

    has_jsonld = bool(re.search(
        r"""<script\b[^>]*type\s*=\s*["']application/ld\+json["']""", document, re.I
    ))
    if not has_jsonld:
        data = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "url": canonical,
            "description": description,
            "inLanguage": "it-IT",
            "isPartOf": {"@type": "WebSite", "name": "Music Archives Italia", "url": base},
        }
        script = '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False
        ).replace("</", "<\\/") + "</script>"
        document = insert_head_content(document, script)

    page_path.write_text(document, encoding="utf-8")
    noindex = any(
        "noindex" in ((get_attr(meta, "content") or "").casefold())
        for meta in re.findall(r"<meta\b[^>]*>", document, re.I)
        if (get_attr(meta, "name") or "").casefold() == "robots"
    )
    return canonical, noindex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()
    artists = validate(json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8")))
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    for artist in artists:
        folder = output / artist["path"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "catalogo.html").write_text(page(artist), encoding="utf-8")

    # Complete per-page metadata in the exact static artifact that GitHub Pages deploys.
    base = "https://salvatoresinatra0001-ux.github.io/music-archives-italia/"
    excluded_parts = {".git", "node_modules", "historic", "storico"}
    html_pages = sorted(
        page for page in output.rglob("*.html")
        if not any(part.lower() in excluded_parts for part in page.relative_to(output).parts)
        and "index-legacy" not in page.name.lower()
        and page.name.lower() != "404.html"
    )
    sitemap_urls = []
    for page_path in html_pages:
        canonical, noindex = ensure_page_seo(page_path, output, base)
        # Only include pages whose declared canonical belongs to this site. Duplicate
        # mirrors with a different canonical host are deliberately omitted.
        if not noindex and canonical and canonical.startswith(base):
            sitemap_urls.append(canonical)
    # Every published page uses the same clean, ornament-free masthead.
    # Inject after the metadata pass so legacy and generated pages are covered.
    import re
    cleanup_tag = '<link rel="stylesheet" href="/music-archives-italia/assets/header-clean.css?v=20261027-no-frame-v2">'
    clean_pages = 0
    for published_page in sorted(output.rglob("*.html")):
        markup = published_page.read_text(encoding="utf-8", errors="replace")
        if "header-clean.css" in markup:
            continue
        closing_head = re.search(r"</head\s*>", markup, re.I)
        if closing_head is None:
            raise ValueError(f"Cannot apply universal header styling: {published_page}")
        markup = markup[:closing_head.start()] + cleanup_tag + "\n" + markup[closing_head.start():]
        published_page.write_text(markup, encoding="utf-8")
        clean_pages += 1
    sitemap_urls = sorted(set(sitemap_urls))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{html.escape(url)}</loc></url>\n" for url in sitemap_urls)
    xml += "</urlset>\n"
    (output / "sitemap.xml").write_text(xml, encoding="utf-8")
    (output / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + base + "sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"Validated {len(artists)} artists; enriched {len(html_pages)} HTML pages; applied clean header on {clean_pages} pages; sitemap: {len(sitemap_urls)} URLs")

if __name__ == "__main__":
    main()
