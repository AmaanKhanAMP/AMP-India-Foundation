import os, json, pymysql, urllib.request
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api = 'https://aif-backend-6jwe.onrender.com'
TABLES = ['hero_banners','home_projects','home_gallery_items','testimonials','featured_events','upcoming_events','gallery_items','navbar_settings','navbar_items','footer_settings','footer_links']
img_fields = ['image_url','banner_image','profile_image','logo_url']

conn = pymysql.connect(
    host=os.getenv('DB_HOST','localhost'),
    port=int(os.getenv('DB_PORT','3306')),
    user=os.getenv('DB_USER','root'),
    password=os.getenv('DB_PASSWORD',''),
    database=os.getenv('DB_NAME','aif_cms'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
)

res = {'local':{}, 'production_public':{}}

def title_of(r):
    for k in ('title','name','label','cta_heading','logo_alt'):
        if r.get(k):
            return r.get(k)
    return f"id={r.get('id')}"

def image_of(r):
    for k in img_fields:
        if r.get(k):
            return r.get(k)
    return ''

with conn.cursor() as cur:
    for t in TABLES:
        cur.execute(f"SELECT * FROM `{t}`")
        rows = cur.fetchall() or []
        alive = [r for r in rows if not r.get('is_deleted')]
        deleted = [r for r in rows if r.get('is_deleted')]
        res['local'][t] = {
            'total': len(rows),
            'alive': len(alive),
            'deleted': len(deleted),
            'rows': [
                {
                    'id': r.get('id'),
                    'title': title_of(r),
                    'image': image_of(r),
                    'status': r.get('status'),
                    'is_deleted': bool(r.get('is_deleted')),
                    'display_order': r.get('display_order'),
                }
                for r in rows
            ]
        }
conn.close()

PUBLIC = {
    'hero_banners':'/api/content/hero-banners',
    'home_projects':'/api/content/home-projects',
    'home_gallery_items':'/api/content/home-gallery',
    'testimonials':'/api/content/testimonials',
    'featured_events':'/api/content/featured-events',
    'upcoming_events':'/api/content/upcoming-events',
    'gallery_items':'/api/content/past-events',
    'navbar_items':'/api/content/navbar-items',
    'footer_links':'/api/content/footer-links',
}
for t,p in PUBLIC.items():
    try:
        with urllib.request.urlopen(api+p, timeout=40) as r:
            j = json.loads(r.read().decode('utf-8'))
        res['production_public'][t] = j.get('data',[])
    except Exception as e:
        res['production_public'][t] = {'error': str(e)}

for t,p in {'navbar_settings':'/api/layout/navbar','footer_settings':'/api/layout/footer'}.items():
    try:
        with urllib.request.urlopen(api+p, timeout=40) as r:
            j = json.loads(r.read().decode('utf-8'))
        data = j.get('data', j)
        res['production_public'][t] = [data] if isinstance(data, dict) else data
    except Exception as e:
        res['production_public'][t] = {'error': str(e)}

out = Path('scripts/_diag_local_vs_prod_public.json')
out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding='utf-8')
print(out)
