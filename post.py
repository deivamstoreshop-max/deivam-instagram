import os, sys, json, time, datetime, urllib.request, urllib.parse, urllib.error
HOST = os.environ.get("IG_API_HOST", "https://graph.facebook.com/v21.0")
TOKEN = os.environ["IG_TOKEN"]; UID = os.environ["IG_USER_ID"]
REPO = os.environ.get("GITHUB_REPOSITORY", "deivamstoreshop-max/deivam-instagram")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{HOST}/{path}"
    req = urllib.request.Request(url + ("?" + data.decode() if method == "GET" else ""), data=None if method == "GET" else data, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API error {e.code}: {e.read().decode()[:500]}")

def wait_ready(cid, tries=20):
    for _ in range(tries):
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED": return
        if st == "ERROR": raise SystemExit(f"container {cid} failed")
        time.sleep(6)
    raise SystemExit(f"container {cid} not ready")

if "--check" in sys.argv:
    print(call("GET", UID, fields="username,media_count")); sys.exit(0)

date = sys.argv[1]
entry = json.load(open(os.path.join(root, "calendar.json"), encoding="utf-8")).get(date)
if not entry: print("no post for", date); sys.exit(0)
if "--dry" in sys.argv: print(entry["caption"]); sys.exit(0)
base = f"https://raw.githubusercontent.com/{REPO}/main/out/{date}"
kids = []
for i in range(1, 7):
    for attempt in range(6):
        try:
            r = call("POST", f"{UID}/media", image_url=f"{base}/{i}.jpg", is_carousel_item="true"); break
        except SystemExit as e:
            if attempt == 5: raise
            print("retry", i, e); time.sleep(20)
    kids.append(r["id"])
for k in kids: wait_ready(k)
car = call("POST", f"{UID}/media", media_type="CAROUSEL", children=",".join(kids), caption=entry["caption"])["id"]
wait_ready(car)
pub = call("POST", f"{UID}/media_publish", creation_id=car)
print("published", pub)
