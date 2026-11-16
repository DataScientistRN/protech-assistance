#!/usr/bin/env python3
"""Bakes the English text from content.js into index.html.

Why: search engines read the HTML they download. Without this, the page is
empty until JavaScript runs, which hurts search ranking. This script fills the
same text into the HTML ahead of time, plus the page title, description,
social tags and structured data (JSON-LD).

Run by hand with:   python3 build.py
It also runs automatically on GitHub whenever content.js changes (see
.github/workflows/build.yml), so editing content.js on github.com is enough.
Safe to run repeatedly: running it twice gives the same result.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SITE_URL = "https://protechassistance.com/"
BUSINESS_NAME = "ProTech Assistance"
BASE_LANG = "en"


# ---- Read content.js -------------------------------------------------------
def load_content(path):
    """Turns the `window.SITE = {...}` object in content.js into a Python dict."""
    src = path.read_text(encoding="utf-8")
    src = src[src.index("=", src.index("window.SITE")) + 1:]
    tokens, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == '"':  # string: copy through the closing quote
            j = i + 1
            while src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            tokens.append(("s", src[i:j + 1]))
            i = j + 1
        elif src.startswith("//", i):
            i = src.find("\n", i)
            i = n if i < 0 else i
        elif src.startswith("/*", i):
            i = src.index("*/", i) + 2
        elif c.isalpha() or c == "_":  # bare word: an object key, or true/false/null
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            k = j
            while k < n and src[k].isspace():
                k += 1
            tokens.append(("s", json.dumps(word)) if k < n and src[k] == ":" else ("o", word))
            i = j
        elif c.isspace() or c == ";":
            i += 1
        else:
            tokens.append(("o", c))
            i += 1
    # JSON does not allow a comma right before } or ]; JavaScript does.
    cleaned = []
    for idx, (kind, text) in enumerate(tokens):
        if kind == "o" and text == "," and idx + 1 < len(tokens) and tokens[idx + 1][1] in ("}", "]"):
            continue
        cleaned.append(text)
    return json.loads("".join(cleaned))


# ---- Helpers ---------------------------------------------------------------
def make_filler(site):
    phone = site["phone"]["display"]
    year = str(date.today().year)

    def fill(text):
        return text.replace("{phone}", phone).replace("{year}", year)

    return fill


def esc(text):
    return html.escape(text, quote=False)


def esc_attr(text):
    return html.escape(text, quote=True)


def rich(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(text))


# ---- Build -----------------------------------------------------------------
def build(page, site):
    t = site["text"][BASE_LANG]
    fill = make_filler(site)
    tel = site["phone"]["tel"]

    def get(key):
        if key not in t:
            sys.exit(f"build.py: content.js has no '{key}' in the '{BASE_LANG}' block")
        return t[key]

    # Plain text elements: <tag data-t="key">...</tag>
    page = re.sub(
        r'(<(?P<tag>\w+)\b[^>]*\bdata-t="(?P<key>\w+)"[^>]*>)[^<]*(</(?P=tag)>)',
        lambda m: m.group(1) + esc(fill(get(m.group("key")))) + m.group(4),
        page,
    )
    # Text with **bold**: <tag data-t-rich="key">...</tag>
    page = re.sub(
        r'(<(?P<tag>\w+)\b[^>]*\bdata-t-rich="(?P<key>\w+)"[^>]*>)[^<]*(</(?P=tag)>)',
        lambda m: m.group(1) + rich(fill(get(m.group("key")))) + m.group(4),
        page,
    )

    # Lists: badges (<li>) and services (cards)
    def list_html(key):
        items = get(key)
        if key == "services":
            return "".join(
                f'<article class="card"><h3>{esc(i["title"])}</h3><p>{esc(i["text"])}</p></article>'
                for i in items
            )
        return "".join(f"<li>{esc(i)}</li>" for i in items)

    page = re.sub(
        r'(<(?P<tag>ul|div)\b[^>]*\bdata-list="(?P<key>\w+)"[^>]*>)(?s:.*?)(</(?P=tag)>)',
        lambda m: m.group(1) + list_html(m.group("key")) + m.group(4),
        page,
    )

    # Phone links
    page = re.sub(r'(data-tel href=")[^"]*(")', lambda m: m.group(1) + "tel:" + tel + m.group(2), page)

    # Title, description and social tags
    title, desc = get("metaTitle"), get("metaDescription")
    page = re.sub(r"<title>.*?</title>", lambda m: f"<title>{esc(title)}</title>", page, flags=re.S)
    for pattern, value in (
        (r'(<meta name="description" content=")[^"]*(")', desc),
        (r'(<meta property="og:title" content=")[^"]*(")', title),
        (r'(<meta property="og:description" content=")[^"]*(")', desc),
    ):
        page = re.sub(pattern, lambda m, v=value: m.group(1) + esc_attr(v) + m.group(2), page)

    # Structured data (tells Google the business details directly)
    data = {
        "@context": "https://schema.org",
        "@type": "AutoRepair",
        "name": BUSINESS_NAME,
        "url": SITE_URL,
        "telephone": tel,
        "description": desc,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Boise",
            "addressRegion": "ID",
            "addressCountry": "US",
        },
        "areaServed": {"@type": "AdministrativeArea", "name": "Greater Boise Area, Idaho"},
        "knowsLanguage": [lang["code"] for lang in site["languages"] if lang["code"] in site["text"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": get("servicesTitle"),
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {"@type": "Service", "name": s["title"], "description": s["text"]},
                }
                for s in get("services")
            ],
        },
    }
    block = (
        "<!-- build:jsonld -->\n"
        '  <script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
        + "\n  </script>\n  <!-- /build:jsonld -->"
    )
    page = re.sub(r"<!-- build:jsonld -->.*?<!-- /build:jsonld -->", lambda m: block, page, flags=re.S)
    return page


def main():
    site = load_content(ROOT / "content.js")
    if "555-0123" in site["phone"]["display"]:
        print("WARNING: content.js still has the placeholder phone number.", file=sys.stderr)
    index = ROOT / "index.html"
    old = index.read_text(encoding="utf-8")
    new = build(old, site)
    if new == old:
        print("index.html already up to date.")
    else:
        index.write_text(new, encoding="utf-8")
        print("index.html updated.")


if __name__ == "__main__":
    main()
