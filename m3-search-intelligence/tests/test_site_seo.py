"""Static SEO hygiene checks for the public M3ALEM-PRO site."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_URL = "https://samani12.github.io/m3alem-pro-site/"


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles = 0
        self.meta_names = {}
        self.canonicals = []
        self.description_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.titles += 1
        if tag == "meta":
            name = (attrs.get("name") or "").lower()
            if name:
                self.meta_names[name] = self.meta_names.get(name, 0) + 1
            if name == "description" and attrs.get("content", "").strip():
                self.description_count += 1
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append(attrs.get("href", ""))


class SiteSEOTests(unittest.TestCase):
    def test_sitemap_urls_resolve_to_existing_html_files(self):
        sitemap = ET.parse(REPO_ROOT / "sitemap.xml").getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text for node in sitemap.findall("sm:url/sm:loc", ns)]
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(SITE_URL), url)
            relative = url[len(SITE_URL):] or "index.html"
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_each_public_page_has_unique_core_metadata(self):
        pages = sorted(REPO_ROOT.glob("*.html"))
        self.assertTrue(pages)
        for path in pages:
            parser = MetadataParser()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(page=path.name):
                self.assertEqual(parser.titles, 1, "one title element required")
                self.assertEqual(parser.description_count, 1, "one non-empty meta description required")
                self.assertEqual(parser.meta_names.get("robots", 0), 1, "one robots directive required")
                self.assertEqual(parser.meta_names.get("theme-color", 0), 1, "one theme-color directive required")
                self.assertEqual(len(parser.canonicals), 1, "one canonical link required")
                self.assertEqual(parser.canonicals[0], SITE_URL + path.name if path.name != "index.html" else SITE_URL)


if __name__ == "__main__":
    unittest.main()
