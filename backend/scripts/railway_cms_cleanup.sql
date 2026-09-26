-- AMP India Foundation — Railway CMS cleanup
-- Database: railway
-- Source of truth: finalized local aif_cms rows (non-deleted, non-Unsplash).
--
-- Run this in MySQL Workbench on the Railway connection.
-- Review the SELECT preview queries first, then run the DELETE block.

USE railway;

-- ========== PREVIEW: rows that will be removed ==========
SELECT 'testimonials' AS tbl, id, name AS title, profile_image AS image, status, is_deleted
FROM testimonials
WHERE is_deleted = 1 OR IFNULL(profile_image,'') LIKE '%unsplash%';

SELECT 'gallery_items' AS tbl, id, title, image_url AS image, status, is_deleted
FROM gallery_items
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

SELECT 'home_projects' AS tbl, id, title, image_url AS image, status, is_deleted
FROM home_projects
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

SELECT 'upcoming_events' AS tbl, id, title, image_url AS image, status, is_deleted
FROM upcoming_events
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

SELECT 'hero_banners' AS tbl, id, title, image_url AS image, status, is_deleted
FROM hero_banners
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

SELECT 'home_gallery_items' AS tbl, id, title, image_url AS image, status, is_deleted
FROM home_gallery_items
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

SELECT 'featured_events' AS tbl, id, title, banner_image AS image, status, is_deleted
FROM featured_events
WHERE is_deleted = 1 OR IFNULL(banner_image,'') LIKE '%unsplash%';

SELECT 'navbar_items' AS tbl, id, label AS title, status, is_deleted
FROM navbar_items
WHERE is_deleted = 1;

SELECT 'footer_links' AS tbl, id, label AS title, status, is_deleted
FROM footer_links
WHERE is_deleted = 1;

-- Extra copies not in the finalized keep-set (title + image)
SELECT id, name, profile_image FROM testimonials
WHERE is_deleted = 0
  AND name NOT IN (
    'Mrinal Kanti Debnath','Yawar Ihsan','Chandrakant Khade',
    'Mohammed Farrok Gheewala','Vikram Singh','Mohammed Ekramuddin Shaikh'
  );

SELECT id, title, image_url FROM gallery_items
WHERE is_deleted = 0
  AND title NOT IN (
    'AMP''s 2nd Srinagar, Kashmir Job Fair',
    'AMP Kolkata Job Fair',
    'AMP Mega Job Fair in Doddaballapur',
    'AMP Mega Job Fair in Nanded',
    'AMP National Talent Search 2025 – Grand Launch',
    'AMP Unity Job Fair at Mumbai 2024'
  );

-- Duplicate singleton rows
SELECT COUNT(*) AS navbar_settings_rows FROM navbar_settings;
SELECT COUNT(*) AS footer_settings_rows FROM footer_settings;

-- ========== COUNTS BEFORE ==========
SELECT 'hero_banners' t, COUNT(*) c FROM hero_banners
UNION ALL SELECT 'home_projects', COUNT(*) FROM home_projects
UNION ALL SELECT 'home_gallery_items', COUNT(*) FROM home_gallery_items
UNION ALL SELECT 'testimonials', COUNT(*) FROM testimonials
UNION ALL SELECT 'featured_events', COUNT(*) FROM featured_events
UNION ALL SELECT 'upcoming_events', COUNT(*) FROM upcoming_events
UNION ALL SELECT 'gallery_items', COUNT(*) FROM gallery_items
UNION ALL SELECT 'navbar_settings', COUNT(*) FROM navbar_settings
UNION ALL SELECT 'navbar_items', COUNT(*) FROM navbar_items
UNION ALL SELECT 'footer_settings', COUNT(*) FROM footer_settings
UNION ALL SELECT 'footer_links', COUNT(*) FROM footer_links;

-- ========== DELETE (run after preview looks correct) ==========
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM testimonials
WHERE is_deleted = 1 OR IFNULL(profile_image,'') LIKE '%unsplash%';

DELETE FROM gallery_items
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

DELETE FROM home_projects
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

DELETE FROM upcoming_events
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

DELETE FROM hero_banners
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

DELETE FROM home_gallery_items
WHERE is_deleted = 1 OR IFNULL(image_url,'') LIKE '%unsplash%';

DELETE FROM featured_events
WHERE is_deleted = 1 OR IFNULL(banner_image,'') LIKE '%unsplash%';

DELETE FROM navbar_items WHERE is_deleted = 1;
DELETE FROM footer_links WHERE is_deleted = 1;

-- If import appended a second copy of finalized rows, keep the lowest id per title.
DELETE t FROM testimonials t
JOIN testimonials t2
  ON t.name = t2.name AND t.id > t2.id AND t.is_deleted = 0 AND t2.is_deleted = 0;

DELETE g FROM gallery_items g
JOIN gallery_items g2
  ON g.title = g2.title AND g.id > g2.id AND g.is_deleted = 0 AND g2.is_deleted = 0;

DELETE h FROM hero_banners h
JOIN hero_banners h2
  ON h.title = h2.title AND h.id > h2.id AND h.is_deleted = 0 AND h2.is_deleted = 0;

DELETE p FROM home_projects p
JOIN home_projects p2
  ON p.title = p2.title AND p.id > p2.id AND p.is_deleted = 0 AND p2.is_deleted = 0;

DELETE x FROM home_gallery_items x
JOIN home_gallery_items y
  ON x.title = y.title AND x.id > y.id AND x.is_deleted = 0 AND y.is_deleted = 0;

DELETE a FROM upcoming_events a
JOIN upcoming_events b
  ON a.title = b.title AND a.id > b.id AND a.is_deleted = 0 AND b.is_deleted = 0;

DELETE a FROM featured_events a
JOIN featured_events b
  ON a.title = b.title AND a.id > b.id AND a.is_deleted = 0 AND b.is_deleted = 0;

DELETE a FROM navbar_items a
JOIN navbar_items b
  ON a.label = b.label AND IFNULL(a.parent_key,'') = IFNULL(b.parent_key,'')
 AND a.id > b.id AND a.is_deleted = 0 AND b.is_deleted = 0;

DELETE a FROM footer_links a
JOIN footer_links b
  ON a.label = b.label AND a.href = b.href AND a.id > b.id AND a.is_deleted = 0 AND b.is_deleted = 0;

-- Extra singleton copies (keep id = 1)
DELETE FROM navbar_settings WHERE id <> 1;
DELETE FROM footer_settings WHERE id <> 1;

SET FOREIGN_KEY_CHECKS = 1;

-- ========== COUNTS AFTER (target alive counts) ==========
-- hero_banners 3 | home_projects 4 | home_gallery_items 6
-- testimonials 6 | featured_events 1 | upcoming_events 5
-- gallery_items 6 | navbar_settings 1 | navbar_items 13
-- footer_settings 1 | footer_links 9
SELECT 'hero_banners' t, COUNT(*) c FROM hero_banners
UNION ALL SELECT 'home_projects', COUNT(*) FROM home_projects
UNION ALL SELECT 'home_gallery_items', COUNT(*) FROM home_gallery_items
UNION ALL SELECT 'testimonials', COUNT(*) FROM testimonials
UNION ALL SELECT 'featured_events', COUNT(*) FROM featured_events
UNION ALL SELECT 'upcoming_events', COUNT(*) FROM upcoming_events
UNION ALL SELECT 'gallery_items', COUNT(*) FROM gallery_items
UNION ALL SELECT 'navbar_settings', COUNT(*) FROM navbar_settings
UNION ALL SELECT 'navbar_items', COUNT(*) FROM navbar_items
UNION ALL SELECT 'footer_settings', COUNT(*) FROM footer_settings
UNION ALL SELECT 'footer_links', COUNT(*) FROM footer_links;
