import sys, os, glob, json
from playwright.sync_api import sync_playwright
date, prefix = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(root, "out", date); os.makedirs(out, exist_ok=True)
logo = next(p for p in (os.path.join(root, "assets", "logo.jpg"), os.path.join(root, "logo.jpg")) if os.path.exists(p))
files = sorted(set(glob.glob(os.path.join(root, "slides", prefix + "-*.html")) + glob.glob(os.path.join(root, prefix + "-*.html"))), key=os.path.basename)
tmp = os.path.join(root, "tmp_render"); os.makedirs(tmp, exist_ok=True)
assert len(files) == 6, f"expected 6 slides for {prefix}, got {len(files)}"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for i, f in enumerate(files, 1):
        html = open(f, encoding="utf-8").read().replace("../assets/logo.jpg", "file://" + logo)
        tf = os.path.join(tmp, os.path.basename(f)); open(tf, "w", encoding="utf-8").write(html)
        pg.goto("file://" + tf)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(800)
        pg.screenshot(path=os.path.join(out, f"{i}.jpg"), type="jpeg", quality=92)
    b.close()
print("rendered", len(files), "->", out)
