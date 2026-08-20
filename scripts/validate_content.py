#!/usr/bin/env python3
import sys
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
