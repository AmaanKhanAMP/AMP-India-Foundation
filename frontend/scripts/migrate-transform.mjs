import fs from 'fs';
import path from 'path';

const root = process.cwd();

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, files);
    else if (/\.(jsx|js)$/.test(entry.name)) files.push(full);
  }
  return files;
}

function ensureUseClient(content) {
  if (content.startsWith('"use client"') || content.startsWith("'use client'")) return content;
  return `"use client";\n\n${content}`;
}

function transformFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const rel = path.relative(root, filePath).replace(/\\/g, '/');

  // Skip if somehow not a component
  let changed = false;

  // react-router → next
  if (content.includes('react-router-dom')) {
    content = content.replace(/import\s*\{([^}]+)\}\s*from\s*['"]react-router-dom['"];?/g, (match, imports) => {
      const names = imports.split(',').map((s) => s.trim()).filter(Boolean);
      const lines = [];
      const linkNames = names.filter((n) => n === 'NavLink' || n === 'Link');
      const hasLocation = names.includes('useLocation');
      if (linkNames.length) {
        lines.push(`import Link from 'next/link';`);
      }
      if (hasLocation) {
        lines.push(`import { usePathname } from 'next/navigation';`);
      }
      return lines.join('\n');
    });

    content = content.replace(/\bNavLink\b/g, 'Link');
    content = content.replace(/\bto=/g, 'href=');
    content = content.replace(/useLocation\(\)/g, 'usePathname()');
    content = content.replace(/const location = usePathname\(\)/g, 'const pathname = usePathname()');
    content = content.replace(/location\.pathname/g, 'pathname');
    content = content.replace(/motion\.create\(Link\)/g, 'motion.create(Link)');
    content = content.replace(/\bMotionNavLink\b/g, 'MotionLink');
    changed = true;
  }

  // Asset imports → public paths
  const assetMap = [
    [/import\s+img\s+from\s+['"][^'"]*logo\.png['"];?/, "const img = '/assets/logo.png';"],
    [/import\s+contact\s+from\s+['"][^'"]*contact\.jpeg['"];?/, "const contact = '/assets/contact.jpeg';"],
    [/import\s+volunteer\s+from\s+['"][^'"]*download\.jpg['"];?/, "const volunteer = '/assets/download.jpg';"],
    [/import\s+medical\s+from\s+['"][^'"]*about\.webp['"];?/, "const medical = '/assets/about.webp';"],
  ];
  for (const [re, replacement] of assetMap) {
    if (re.test(content)) {
      content = content.replace(re, replacement);
      changed = true;
    }
  }

  // Page/component relative import fixes
  if (rel === 'components/pages/Home.jsx') {
    content = content
      .replace(/from\s+['"]\.\/home-section\/Hero['"]/, "from '@/components/home/Hero'")
      .replace(/from\s+['"]\.\/home-section\/Impact['"]/, "from '@/components/home/Impact'")
      .replace(/from\s+['"]\.\/home-section\/Preview['"]/, "from '@/components/home/Preview'")
      .replace(/from\s+['"]\.\/home-section\/Projects['"]/, "from '@/components/home/Projects'")
      .replace(/from\s+['"]\.\/home-section\/Testimonial['"]/, "from '@/components/home/Testimonial'")
      .replace(/from\s+['"]\.\/home-section\/Event['"]/, "from '@/components/home/Event'");
    changed = true;
  }

  if (rel === 'components/pages/Events.jsx') {
    content = content
      .replace(/from\s+['"]\.\.\/components\/events\//g, "from '@/components/events/")
      .replace(/import\s+['"]\.\/Events\.css['"]/, "import '@/styles/Events.css'");
    changed = true;
  }

  // All interactive components need use client
  const needsClient =
    /useState|useEffect|useRef|framer-motion|from 'next\/link'|from "next\/link"|usePathname|onClick|document\.|window\./.test(
      content
    );

  if (needsClient) {
    const next = ensureUseClient(content);
    if (next !== content) {
      content = next;
      changed = true;
    }
  }

  if (changed || needsClient) {
    fs.writeFileSync(filePath, content);
    console.log('updated', rel);
  }
}

const files = walk(path.join(root, 'components'));
for (const file of files) transformFile(file);
console.log('Done transforming', files.length, 'files');
