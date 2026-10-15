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
    pages = ["index.html"]
    for artist in artists:
        pages.extend(f"{artist['path']}/{filename}" for filename in
                     ("index.html", "profilo.html", "discografia.html", "singoli.html",
                      "collaborazioni.html", "ricerca.html", "catalogo.html"))
    pages.append("heartagram-italia/index.html")
    missing = [path for path in pages if not (output / path).is_file()]
    if missing:
        raise ValueError(f"Missing required pages: {missing}")
    base = "https://salvatoresinatra0001-ux.github.io/music-archives-italia/"
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{html.escape(base + quote(path))}</loc></url>\n" for path in pages)
    xml += "</urlset>\n"
    (output / "sitemap.xml").write_text(xml, encoding="utf-8")
    (output / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + base + "sitemap.xml\n", encoding="utf-8")
    print(f"Validated {len(artists)} artist manifests and generated {len(pages)} sitemap entries")

if __name__ == "__main__":
    main()
