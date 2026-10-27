#!/usr/bin/env python3
"""Fail deployment when generated HTML has visible escape sequences or duplicate heads."""
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

INERT = {"script", "style", "pre", "code", "textarea", "noscript"}


class DocumentAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heads = 0
        self.head_ends = 0
        self.bodies = 0
        self.body_ends = 0
        self.inert = 0
        self.visible_escapes = []

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.heads += 1
        if tag == "body":
            self.bodies += 1
        if tag in INERT:
            self.inert += 1

    def handle_endtag(self, tag):
        if tag == "head":
            self.head_ends += 1
        if tag == "body":
            self.body_ends += 1
        if tag in INERT:
            self.inert = max(0, self.inert - 1)

    def handle_data(self, data):
        # Python code, embedded JSON and formatting examples are not visible content.
        if not self.inert and "\\n" in data:
            self.visible_escapes.append(data[:90])


def audit_page(path):
    page = path.read_text(encoding="utf-8", errors="replace")
    parser = DocumentAudit()
    parser.feed(page)
    errors = []
    if parser.heads != 1 or parser.head_ends != 1:
        errors.append(f"head elements: {parser.heads} open / {parser.head_ends} closed")
    if parser.bodies != 1 or parser.body_ends != 1:
        errors.append(f"body elements: {parser.bodies} open / {parser.body_ends} closed")
    if parser.visible_escapes:
        errors.append(f"visible literal newline escape(s): {parser.visible_escapes[:2]}")
    if re.search(r"<head\b", page[:30], flags=re.I):
        errors.append("a head tag precedes the document root")
    if "header-clean.css?v=20261027-no-frame-v2" not in page:
        errors.append("missing global frame-removal stylesheet")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()
    pages = sorted(Path(args.output).rglob("*.html"))
    if not pages:
        raise SystemExit("No HTML pages found")
    faults = [(str(p), errors) for p in pages if (errors := audit_page(p))]
    for path, issues in faults[:40]:
        print(f"INVALID: {path}: " + "; ".join(issues))
    if faults:
        raise SystemExit(f"Deployment blocked: {len(faults)}/{len(pages)} HTML pages malformed")
    print(f"HTML integrity OK: {len(pages)} pages, one head/body each, no visible escape text")


if __name__ == "__main__":
    main()
