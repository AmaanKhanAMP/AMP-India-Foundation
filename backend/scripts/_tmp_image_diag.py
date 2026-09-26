import os, json, pymysql, urllib.request, urllib.error
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api = 'https://aif-backend-6jwe.onrender.com'
conn = pymysql.connect(host=os.getenv('DB_HOST','localhost'),port=int(os.getenv('DB_PORT','3306')),user=os.getenv('DB_USER','root'),password=os.getenv('DB_PASSWORD',''),database=os.getenv('DB_NAME','aif_cms'),charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
UPLOAD_ROOT = Path('uploads').resolve()

def fetch_local(table, img_field='image_url'):
    with conn.cursor() as cur:
        cur.execute(f"SELECT id, title, {img_field} AS image_url, display_order, status, is_deleted FROM `{table}`")
        rows = cur.fetchall() or []
    return [r for r in rows if not r.get('is_deleted')]

def fetch_prod(path):
    with urllib.request.urlopen(api + path, timeout=40) as r:
        return json.loads(r.read().decode('utf-8')).get('data',[])

def exists_prod(url_path):
    url = api + url_path if url_path.startswith('/') else url_path
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return True, r.status
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception:
        return False, None

local_hero = fetch_local('hero_banners')
local_proj = fetch_local('home_projects')
local_gallery = fetch_local('home_gallery_items')
prod_hero = fetch_prod('/api/content/hero-banners')
prod_proj = fetch_prod('/api/content/home-projects')
prod_gallery = fetch_prod('/api/content/home-gallery')

prod_maps = {
 'hero_banners': {r.get('title'): r.get('image_url') for r in prod_hero},
 'home_projects': {r.get('title'): r.get('image_url') for r in prod_proj},
 'home_gallery_items': {r.get('title'): r.get('image_url') for r in prod_gallery},
}

rows=[]
for table,items in [('hero_banners',local_hero),('home_projects',local_proj),('home_gallery_items',local_gallery)]:
    for r in sorted(items,key=lambda x:(x.get('display_order') or 0,x.get('id') or 0)):
        local_url=r.get('image_url') or ''
        prod_url=prod_maps.get(table,{}).get(r.get('title'))
        local_exists=False
        if local_url.startswith('/uploads/'):
            local_exists=(UPLOAD_ROOT / local_url.replace('/uploads/','')).exists()
        prod_exists,code = exists_prod(prod_url) if prod_url else (False,None)
        rows.append({
            'table':table,
            'record':r.get('title'),
            'local_image_url':local_url,
            'railway_image_url':prod_url,
            'local_file_exists':local_exists,
            'railway_file_exists':prod_exists,
            'http_status':code,
            'status':'OK' if (local_exists and prod_exists) else 'MISSING_IN_PROD' if local_exists and not prod_exists else 'LOCAL_MISSING'
        })

conn.close()
out=Path('scripts/_homepage_image_matrix.json')
out.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
print(out)
