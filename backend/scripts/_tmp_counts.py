import os, pymysql
from dotenv import load_dotenv
load_dotenv()
conn=pymysql.connect(host=os.getenv('DB_HOST','localhost'),port=int(os.getenv('DB_PORT','3306')),user=os.getenv('DB_USER','root'),password=os.getenv('DB_PASSWORD',''),database=os.getenv('DB_NAME','aif_cms'),charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
tables=['hero_banners','home_projects','home_gallery_items','testimonials','featured_events','upcoming_events','gallery_items','navbar_items','footer_links']
with conn.cursor() as cur:
  for t in tables:
    cur.execute(f"SELECT COUNT(*) c FROM `{t}` WHERE is_deleted=0 AND (status='published' OR status IS NULL)")
    c=cur.fetchone()['c']
    print(f"{t}: local_published={c}")
conn.close()
