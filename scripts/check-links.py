#!/usr/bin/env python3
"""Light link check for the CV site: local files must exist; external URLs are probed gently."""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
HREF_RE = re.compile(r'(?:href|src)="([^"]+)"')

# LinkedIn often blocks automated HEAD/GET with 999/403.
SOFT_HOSTS = ("linkedin.com", "www.linkedin.com")
TIMEOUT = 12
USER_AGENT = "sebbass28-cv-linkcheck/1.0"


def is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def local_path(url: str) -> Path | None:
    if url.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    if is_external(url):
        return None
    clean = url.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    return ROOT / clean


def check_external(url: str) -> str | None:
    headers = {"User-Agent": USER_AGENT}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                if response.status >= 400:
                    return f"{url} -> HTTP {response.status}"
                return None
        except urllib.error.HTTPError as error:
            if error.code in {401, 403, 405, 429, 999} or any(
                host in url for host in SOFT_HOSTS
            ):
                # Light check: treat anti-bot / auth responses as acceptable.
                return None
            if method == "HEAD" and error.code in {400, 404, 405}:
                continue
            return f"{url} -> HTTP {error.code}"
        except Exception as error:  # noqa: BLE001 — report any network failure
            if method == "HEAD":
                continue
            return f"{url} -> {error}"
    return None


def main() -> int:
    urls = []
    for match in HREF_RE.findall(HTML):
        if match not in urls:
            urls.append(match)

    # Also collect same-page anchors and confirm their ids exist.
    anchors = [u[1:] for u in urls if u.startswith("#") and len(u) > 1]
    html_ids = set(re.findall(r'id="([^"]+)"', HTML))

    failures: list[str] = []

    for url in urls:
        if url.startswith("#"):
            target = url[1:]
            if target and target not in html_ids:
                failures.append(f"Missing in-page target: {url}")
            continue

        path = local_path(url)
        if path is not None and not path.exists():
            failures.append(f"Missing local file: {url}")
            continue

        if is_external(url) and "sebbass28.github.io" not in url:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            # Origin-only URLs (rel=preconnect) often 404; only probe paths.
            if parsed.path not in ("", "/"):
                problem = check_external(url)
                if problem:
                    failures.append(problem)

    # Confirm Open Graph image and PDF exist even if only referenced as absolute URLs later.
    required = [
        ROOT / "cv" / "CV_Juan_Agudelo_Castrillon.pdf",
        ROOT / "og-image.png",
        ROOT / "favicon.svg",
        ROOT / "styles.css",
        ROOT / "script.js",
    ]
    for path in required:
        if not path.exists():
            failures.append(f"Missing required file: {path.relative_to(ROOT)}")

    if failures:
        print("Comprobación de enlaces: errores")
        for item in failures:
            print(f" - {item}")
        return 1

    print(f"Comprobación de enlaces: OK ({len(urls)} referencias, {len(anchors)} anclas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
