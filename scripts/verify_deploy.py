#!/usr/bin/env python3
import sys
from urllib.request import Request, urlopen

base = (sys.argv[1] if len(sys.argv) > 1 else "https://honorlin.github.io/taiwan-family-life/").rstrip("/")
paths = ("/", "/articles/", "/about/", "/safety/", "/articles/2026/08/21/toddler-mealtime-no-pressure/")
for path in paths:
    url = base + path
    with urlopen(Request(url, headers={"User-Agent": "taiwan-family-life-check/1.0"}), timeout=20) as response:
        body = response.read().decode("utf-8", "ignore")
        if response.status != 200 or "台灣親子好生活" not in body:
            raise SystemExit(f"FAILED {url}: {response.status}")
        print(f"OK {url}")
