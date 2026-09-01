#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from urllib.parse import urlparse
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
POLICY = yaml.safe_load((ROOT / "automation/content-policy.yml").read_text())
CATEGORIES = {x["key"] for x in yaml.safe_load((ROOT / "_data/site.yml").read_text())["categories"]}
TRUSTED = tuple(yaml.safe_load((ROOT / "automation/trusted-sources.yml").read_text())["approved_domains"])
REQUIRED_META = ("title", "description", "category", "category_name", "age_range", "risk_level", "image", "image_alt", "image_caption", "sources", "photo_credits")

def trusted(url):
    host = (urlparse(str(url)).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in TRUSTED)

def validate(path):
    text = path.read_text(encoding="utf-8")
    errors = []
    if not text.startswith("---"):
        return ["missing front matter"]
    _, raw, body = text.split("---", 2)
    meta = yaml.safe_load(raw) or {}
    for key in REQUIRED_META:
        if not meta.get(key): errors.append(f"missing {key}")
    if meta.get("category") not in CATEGORIES: errors.append("unknown category")
    if meta.get("risk_level") not in POLICY["auto_publish"]["allowed_risk_levels"]: errors.append("risk is not auto-publishable")
    for heading in POLICY["required_sections"]:
        if heading not in body: errors.append(f"missing section: {heading}")
    for phrase in POLICY["blocked_phrases"]:
        if phrase in text: errors.append(f"blocked phrase: {phrase}")
    sources = meta.get("sources") or []
    if len(sources) < POLICY["auto_publish"]["minimum_sources"]: errors.append("not enough sources")
    for source in sources:
        if not source.get("title") or not trusted(source.get("url")): errors.append("invalid or untrusted source")
    image = ROOT / str(meta.get("image", "")).lstrip("/")
    if not image.exists(): errors.append("image missing")
    else:
        with Image.open(image) as im:
            if im.size != (1200, 630): errors.append(f"cover must be 1200x630, got {im.size}")
    credits = meta.get("photo_credits") or []
    modern_photo_standard = meta.get("editorial_standard") == "real_photo_v2"
    if modern_photo_standard:
        if len(re.sub(r"\s", "", body)) < 1200:
            errors.append("body must contain at least 1200 non-whitespace characters")
        if len(credits) < 3:
            errors.append("at least three photo credits required")

        displayed = {str(meta.get("image", ""))}
        displayed.update(re.findall(r'<img[^>]+src="\{\{\s*[\'\"]([^\'\"]+)[\'\"]\s*\|\s*relative_url\s*\}\}"', body))
        if len(displayed) < 3:
            errors.append("at least three local images must be displayed")

        credited_files = {str(x.get("file", "")) for x in credits}
        for shown in displayed:
            if shown not in credited_files:
                errors.append(f"displayed image lacks photo credit: {shown}")

        for credit in credits:
            for key in ("file", "creator", "source", "license", "license_url", "modifications", "alt", "caption"):
                if not credit.get(key): errors.append(f"incomplete photo credit: {key}")
            credit_file = ROOT / str(credit.get("file", "")).lstrip("/")
            if not credit_file.exists():
                errors.append(f"credited image missing: {credit.get('file', '')}")
                continue
            with Image.open(credit_file) as im:
                expected = (1200, 630) if str(credit.get("file")) == str(meta.get("image")) else ((1200, 800), (1200, 630))
                if isinstance(expected[0], tuple):
                    if im.size not in expected: errors.append(f"inline image has invalid size: {credit.get('file')}")
                elif im.size != expected:
                    errors.append(f"cover must be 1200x630, got {im.size}")
    else:
        if len(credits) != 1: errors.append("exactly one cover photo credit required")
        else:
            for key in ("file", "creator", "source", "license", "license_url", "modifications"):
                if not credits[0].get(key): errors.append(f"incomplete photo credit: {key}")
    return sorted(set(errors))

targets = [Path(x) for x in sys.argv[1:]] or sorted((ROOT / "_posts").glob("*.md"))
failed = False
for target in targets:
    errors = validate(target)
    if errors:
        failed = True
        print(f"{target}: {'; '.join(errors)}", file=sys.stderr)
if failed: raise SystemExit(1)
print(f"Validated {len(targets)} article(s).")
