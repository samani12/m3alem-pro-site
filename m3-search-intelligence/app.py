#!/usr/bin/env python3
"""M3 Search Intelligence local dashboard. Python standard library only."""
from __future__ import annotations
import csv, io, json, os, sqlite3, threading, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from m3si.engine import crawl_site, score_opportunity, normalize_url
from m3si.marrakech import analyze_queries
from m3si.csv_import import parse_number

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "m3si.sqlite3"
SITE_URL = os.environ.get("M3SI_SITE_URL", "https://samani12.github.io/m3alem-pro-site/")
HOST, PORT = "127.0.0.1", int(os.environ.get("M3SI_PORT", "8765"))
LOCK = threading.Lock()

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS pages (
        url TEXT PRIMARY KEY, title TEXT, description TEXT, h1 TEXT,
        canonical TEXT, word_count INTEGER, status INTEGER, crawled_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS queries (
        query TEXT PRIMARY KEY, clicks REAL, impressions REAL, ctr REAL,
        position REAL, source TEXT, imported_at TEXT
    )""")
    c.commit()
    return c

def esc(s):
    return (str(s or "").replace("&","&amp;").replace("<","&lt;")
            .replace(">","&gt;").replace('"',"&quot;").replace("'","&#39;"))

def page():
    with connect() as c:
        pages = c.execute("SELECT * FROM pages ORDER BY crawled_at DESC LIMIT 100").fetchall()
        queries = c.execute("SELECT * FROM queries ORDER BY impressions DESC LIMIT 100").fetchall()
    rows = "".join(f"<tr><td>{esc(r['query'])}</td><td>{r['clicks'] or 0:g}</td><td>{r['impressions'] or 0:g}</td><td>{(r['ctr'] or 0):.1%}</td><td>{(r['position'] or 0):.1f}</td><td>{score_opportunity(r['impressions'] or 0,r['ctr'] or 0,r['position'] or 0)}</td></tr>" for r in queries)
    local_rows = analyze_queries([dict(r) for r in queries])
    local_html = "".join(
        f"<tr><td>{esc(x['query'])}</td><td>{x['score']:.1f}/100</td><td>{esc(x['intent'])}</td><td>{esc(', '.join(x['services']))}</td><td>{esc(x['recommended_page'] or 'تحتاج تصنيف يدوي')}</td></tr>"
        for x in local_rows[:30]
    )
    page_rows = "".join(f"<tr><td><a href='{esc(r['url'])}' target='_blank' rel='noopener'>{esc(r['url'])}</a></td><td>{esc(r['title'])}</td><td>{r['word_count'] or 0}</td><td>{r['status'] or 0}</td></tr>" for r in pages)
    return f"""<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>M3 Search Intelligence</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#0b1424;color:#eef3fa;font:15px system-ui}}main{{max-width:1100px;margin:auto;padding:24px}}
header,.panel{{background:#14243b;border:1px solid #263b58;border-radius:16px;padding:20px;margin-bottom:18px}}
h1{{margin:0 0 8px;color:#e8c78b}}h2{{font-size:19px}}p,.muted{{color:#aebdd0}}button{{background:#d7b477;color:#101a29;border:0;border-radius:8px;padding:10px 16px;font-weight:700;cursor:pointer}}
input{{padding:9px;border-radius:8px;border:1px solid #49617d;background:#0c192b;color:white;max-width:100%}}
table{{width:100%;border-collapse:collapse;display:block;overflow-x:auto;white-space:nowrap}}td,th{{padding:10px;border-bottom:1px solid #30445e;text-align:right}}th{{color:#e8c78b}}
a{{color:#f1d6a4}}.actions{{display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
</style><main><header><h1>M3 Search Intelligence</h1><p>مركز ذكاء البحث وتحسين الظهور — M3ALEM-PRO</p><div class="muted">الموقع: {esc(SITE_URL)} · البيانات محفوظة محلياً على جهازك</div></header>
<section class="panel"><h2>1) فحص صفحات الموقع</h2><p>فحص محدود وآمن لنفس النطاق، مع احترام robots.txt.</p><form method="post" action="/crawl"><button>ابدأ الفحص</button></form></section>
<section class="panel"><h2>2) استيراد بيانات البحث CSV</h2><p>حمّل تصدير Queries من Google Search Console أو Bing Webmaster Tools.</p><form class="actions" method="post" action="/import" enctype="multipart/form-data"><input type="file" name="csvfile" accept=".csv,text/csv" required><button>استيراد وتحليل</button></form></section>
<section class="panel"><h2>3) فرص الكلمات المفتاحية</h2><p class="muted">النقاط ترتيب أولويات داخلي وليست توقعاً للترتيب أو عدد الزبائن.</p><table><thead><tr><th>الكلمة</th><th>النقرات</th><th>الظهور</th><th>CTR</th><th>الموضع</th><th>الأولوية</th></tr></thead><tbody>{rows or '<tr><td colspan="6">مازال ما دخلات حتى بيانات. صدّر CSV من Search Console.</td></tr>'}</tbody></table></section>
<section class="panel"><h2>4) M3 Marrakech SEO Intelligence</h2><p class="muted">ترتيب فرص محلية حسب نية الشراء، ارتباط الخدمة، الظهور وCTR. هذا مؤشر أولوية وليس توقع ترتيب.</p><table><thead><tr><th>الكلمة</th><th>الأولوية</th><th>النية</th><th>الخدمة</th><th>الصفحة المقترحة</th></tr></thead><tbody>{local_html or '<tr><td colspan="5">أدخل بيانات Queries من Search Console لتفعيل التحليل.</td></tr>'}</tbody></table></section>
<section class="panel"><h2>5) الصفحات التي تم فحصها</h2><table><thead><tr><th>الرابط</th><th>العنوان</th><th>الكلمات</th><th>HTTP</th></tr></thead><tbody>{page_rows or '<tr><td colspan="4">مازال ما تفحص حتى صفحة.</td></tr>'}</tbody></table></section>
<p class="muted">M3 Marrakech SEO Engine V1 · لا توجد مفاتيح API داخل المشروع · لا يتم تعديل الموقع تلقائياً.</p></main></html>"""

class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data))); self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path == "/":
            return self.send(200, page())
        if self.path == "/health":
            return self.send(200, json.dumps({"ok":True,"version":"0.2"}), "application/json")
        return self.send(404, "Not found")
    def do_POST(self):
        if self.path == "/crawl":
            try:
                results = crawl_site(SITE_URL, max_pages=30, delay=0.5)
                with LOCK, connect() as c:
                    for p in results:
                        c.execute("""INSERT OR REPLACE INTO pages VALUES (?,?,?,?,?,?,?,?)""",
                          (p["url"],p["title"],p["description"],p["h1"],p["canonical"],p["word_count"],p["status"],datetime.now(timezone.utc).isoformat()))
                return self.send(200, "<meta charset='utf-8'><p>فحصنا "+str(len(results))+" صفحة. <a href='/'>رجوع للوحة</a></p>")
            except Exception as e:
                return self.send(400, "<meta charset='utf-8'>تعذر الفحص: "+esc(e)+" <a href='/'>رجوع</a>")
        if self.path == "/import":
            length = int(self.headers.get("Content-Length","0"))
            if length <= 0 or length > 5_000_000:
                return self.send(400, "Invalid upload size")
            body = self.rfile.read(length)
            ctype = self.headers.get("Content-Type","")
            if "multipart/form-data" not in ctype:
                return self.send(400, "CSV multipart upload required")
            from email.parser import BytesParser
            from email.policy import default
            msg = BytesParser(policy=default).parsebytes(b"Content-Type: "+ctype.encode()+b"\r\nMIME-Version: 1.0\r\n\r\n"+body)
            part = next((p for p in msg.iter_parts() if p.get_param("name",header="content-disposition")=="csvfile"),None)
            if part is None: return self.send(400,"CSV file missing")
            raw = part.get_payload(decode=True) or b""
            try: text = raw.decode("utf-8-sig")
            except UnicodeDecodeError: return self.send(400,"CSV must be UTF-8")
            reader = csv.DictReader(io.StringIO(text))
            def get(row,*keys):
                low = {str(k).strip().lower():v for k,v in row.items() if k}
                for k in keys:
                    if k in low: return low[k]
                return ""
            count=0
            with LOCK, connect() as c:
                for row in reader:
                    q=get(row,"query","queries","requête","requêtes","requete","requetes","top queries","keyword","search query","الاستعلامات","طلبات البحث")
                    if not q.strip(): continue
                    clicks=parse_number(get(row,"clicks","clics","النقرات"))
                    impr=parse_number(get(row,"impressions","مرات الظهور"))
                    ctrv=get(row,"ctr","taux de clics","taux de clic","نسبة النقر")
                    ctr=parse_number(ctrv)
                    if "%" in str(ctrv) or ctr>1: ctr/=100
                    pos=parse_number(get(row,"position","average position","avg position","position moyenne","الموضع","متوسط الموضع"))
                    c.execute("INSERT OR REPLACE INTO queries VALUES (?,?,?,?,?,?,?)",
                      (q.strip(),clicks,impr,ctr,pos,"CSV",datetime.now(timezone.utc).isoformat()))
                    count+=1
            return self.send(200, f"<meta charset='utf-8'><p>تم استيراد {count} كلمة. <a href='/'>شوف النتائج</a></p>")
        return self.send(404,"Not found")
    def log_message(self, *_): pass

if __name__ == "__main__":
    print(f"M3SI listening on http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
