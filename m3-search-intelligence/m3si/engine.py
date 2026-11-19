"""Safe same-host crawler and explainable opportunity scoring."""
from __future__ import annotations
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.robotparser import RobotFileParser
from urllib.error import URLError, HTTPError
import re, time

UA = "M3SearchIntelligence/0.2 (+local SEO audit; respectful crawler)"


def normalize_url(url):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise ValueError("Only HTTP(S) URLs are allowed")
    return urldefrag(url)[0]


def internal_links(page_url, hrefs, host):
    """Return valid HTTP(S) links for this host; ignore mailto/js/tel and malformed hrefs."""
    found = []
    for href in hrefs:
        try:
            candidate = normalize_url(urljoin(page_url, href))
            parsed = urlparse(candidate)
        except (TypeError, ValueError):
            continue
        if parsed.hostname == host and parsed.scheme in ("http", "https"):
            found.append(candidate)
    return found


class SameHostRedirect(HTTPRedirectHandler):
    def __init__(self, host):
        self.host = host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlparse(newurl)
        if target.hostname != self.host or target.scheme not in ("http", "https"):
            raise HTTPError(newurl, code, "Cross-host redirect blocked", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = False
        self.h1 = False
        self.desc = ""
        self.canonical = ""
        self.t = []
        self.h = []
        self.words = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.title = True
        if tag == "h1":
            self.h1 = True
        if tag == "meta" and a.get("name", "").lower() == "description":
            self.desc = a.get("content", "")
        if tag == "link" and "canonical" in a.get("rel", "").lower():
            self.canonical = a.get("href", "")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.title = False
        if tag == "h1":
            self.h1 = False

    def handle_data(self, data):
        s = data.strip()
        if not s:
            return
        if self.title:
            self.t.append(s)
        if self.h1:
            self.h.append(s)
        self.words.extend(re.findall(r"\w+", s, flags=re.UNICODE))


def crawl_site(site_url, max_pages=30, delay=0.5, timeout=8):
    if not isinstance(max_pages, int) or max_pages < 1:
        raise ValueError("max_pages must be a positive integer")
    max_pages = min(max_pages, 100)
    timeout = max(1, min(float(timeout), 30))
    delay = max(0, min(float(delay), 5))

    start = normalize_url(site_url)
    base = urlparse(start)
    host = base.hostname
    robots_url = f"{base.scheme}://{host}/robots.txt"
    rp = RobotFileParser()
    try:
        req = Request(robots_url, headers={"User-Agent": UA})
        with build_opener(SameHostRedirect(host)).open(req, timeout=timeout) as r:
            rp.parse(r.read(200000).decode("utf-8", "replace").splitlines())
    except Exception:
        # If robots.txt cannot be read, fail closed rather than crawling blindly.
        return []

    opener = build_opener(SameHostRedirect(host))
    queue = [start]
    seen = set()
    results = []
    while queue and len(results) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        p = urlparse(url)
        if p.hostname != host or p.scheme not in ("http", "https"):
            continue
        if not rp.can_fetch(UA, url):
            continue
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
            with opener.open(req, timeout=timeout) as response:
                status = response.status
                ctype = response.headers.get("Content-Type", "")
                if "text/html" not in ctype.lower():
                    continue
                raw = response.read(1_000_000)
            parser = Extract()
            parser.feed(raw.decode("utf-8", "replace"))
            results.append({
                "url": url,
                "title": " ".join(parser.t),
                "description": parser.desc,
                "h1": " ".join(parser.h),
                "canonical": urljoin(url, parser.canonical) if parser.canonical else "",
                "word_count": len(parser.words),
                "status": status,
            })
            for nxt in internal_links(url, parser.links, host):
                if nxt not in seen and len(queue) < max_pages * 4:
                    queue.append(nxt)
            time.sleep(delay)
        except (URLError, HTTPError, TimeoutError, ValueError):
            continue
    return results


def score_opportunity(impressions, ctr, position):
    """0-100 heuristic: high impressions, CTR headroom, attainable positions."""
    imp = max(0, float(impressions or 0))
    ctr = max(0, min(1, float(ctr or 0)))
    pos = max(0, float(position or 0))
    volume = min(40, 40 * (1 - 2.71828 ** (-imp / 500)))
    ctr_gap = min(35, max(0, 0.08 - ctr) * 437.5)
    position_fit = 25 if 3 <= pos <= 20 else (15 if 1 <= pos < 3 else (10 if 20 < pos <= 40 else 0))
    return round(min(100, volume + ctr_gap + position_fit))
