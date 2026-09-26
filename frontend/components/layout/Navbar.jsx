"use client";

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { resolveSiteAssetUrl } from '@/lib/contentApi';
import { toCanonicalPath } from '@/lib/pageMetadata';

const FALLBACK_NAVBAR = {
  logo_url: '/assets/logo.png',
  logo_alt: 'AMP Logo',
  logo_link: '/',
};

const FALLBACK_ITEMS = [
  { id: 1, label: 'HOME', href: '/', itemType: 'link', itemKey: null, parentKey: null, order: 1 },
  { id: 2, label: 'ABOUT US', href: '/about', itemType: 'link', itemKey: null, parentKey: null, order: 2 },
  { id: 3, label: 'PROJECTS', href: '/projects', itemType: 'dropdown', itemKey: 'projects', parentKey: null, order: 3 },
  { id: 4, label: 'Education', href: '/projects/education', itemType: 'link', itemKey: null, parentKey: 'projects', order: 4 },
  { id: 5, label: 'Medical Relief', href: '/projects/medical', itemType: 'link', itemKey: null, parentKey: 'projects', order: 5 },
  { id: 6, label: 'Employment Support', href: '/projects/employment', itemType: 'link', itemKey: null, parentKey: 'projects', order: 6 },
  { id: 7, label: 'Economic Empowerment', href: '/projects/empowerment', itemType: 'link', itemKey: null, parentKey: 'projects', order: 7 },
  { id: 8, label: 'Student Mentorship', href: '/projects/mentorship', itemType: 'link', itemKey: null, parentKey: 'projects', order: 8 },
  { id: 9, label: 'Employment Training', href: '/projects/training', itemType: 'link', itemKey: null, parentKey: 'projects', order: 9 },
  { id: 10, label: 'EVENTS', href: '/events', itemType: 'link', itemKey: null, parentKey: null, order: 10 },
  { id: 11, label: 'VOLUNTEER', href: '/volunteer', itemType: 'link', itemKey: null, parentKey: null, order: 11 },
  { id: 12, label: 'SUPPORT US', href: '/support-us', itemType: 'link', itemKey: null, parentKey: null, order: 12 },
  { id: 13, label: 'CONTACT', href: '/contact', itemType: 'link', itemKey: null, parentKey: null, order: 13 },
];

function buildNavTree(items) {
  const sorted = [...items].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  const roots = sorted.filter((item) => !item.parentKey);
  return roots.map((root) => {
    const normalized =
      root.itemType === 'dropdown' && root.itemKey === 'projects'
        ? { ...root, href: '/projects' }
        : root;
    return {
      ...normalized,
      children:
        normalized.itemType === 'dropdown' && normalized.itemKey
          ? sorted.filter((item) => item.parentKey === normalized.itemKey)
          : [],
    };
  });
}

const Navbar = ({ settings, items }) => {
  const brand = settings ? { ...FALLBACK_NAVBAR, ...settings } : FALLBACK_NAVBAR;
  const rawItems = Array.isArray(items) ? items : FALLBACK_ITEMS;
  const menuTree = useMemo(() => buildNavTree(rawItems), [rawItems]);

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [openDropdownKey, setOpenDropdownKey] = useState(null);
  const [expandedKey, setExpandedKey] = useState(null);

  const logoSrc = resolveSiteAssetUrl(brand.logo_url || FALLBACK_NAVBAR.logo_url);
  const logoAlt = brand.logo_alt || FALLBACK_NAVBAR.logo_alt;
  const logoLink = toCanonicalPath(brand.logo_link || FALLBACK_NAVBAR.logo_link);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((open) => {
      if (open) setExpandedKey(null);
      return !open;
    });
  };

  const handleLinkClick = () => {
    setIsMobileMenuOpen(false);
    setExpandedKey(null);
  };

  const toggleProjectsSubmenu = (itemKey) => {
    setExpandedKey((key) => (key === itemKey ? null : itemKey));
  };

  return (
    <nav className="humanity-navbar">
      <div className="navbar-container">
        
        {/* AMP India Foundation Logo Section */}
        <div className="navbar-brand-amp">
          <Link href={logoLink} onClick={handleLinkClick}>
            <img src={logoSrc} className="amp-logo" alt={logoAlt} />
          </Link>
        </div>

        {/* Animated hamburger ↔ close toggle (mobile only) */}
        <button
          type="button"
          className={`mobile-menu-btn${isMobileMenuOpen ? ' is-open' : ''}`}
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMobileMenuOpen}
          aria-controls="primary-mobile-nav"
        >
          <span className="mobile-menu-icon" aria-hidden="true">
            <Menu className="mobile-icon mobile-icon--menu" size={22} strokeWidth={2.25} />
            <X className="mobile-icon mobile-icon--close" size={22} strokeWidth={2.25} />
          </span>
        </button>

        {/* Navigation Links */}
        <div
          id="primary-mobile-nav"
          className={`navbar-menu ${isMobileMenuOpen ? 'active' : ''}`}
        >
          <ul className="nav-links">
            {menuTree.map((item) => {
              if (item.itemType === 'dropdown') {
                const isExpanded = expandedKey === item.itemKey;
                const isHoverOpen = openDropdownKey === item.itemKey;
                return (
                  <li
                    key={item.id}
                    className={`dropdown${isExpanded ? ' is-expanded' : ''}`}
                    onMouseEnter={() => setOpenDropdownKey(item.itemKey)}
                    onMouseLeave={() => setOpenDropdownKey(null)}
                  >
                    {/*
                      Projects label navigates to /projects (all viewports).
                      Chevron alone expands the submenu on mobile — previously
                      preventDefault on the whole link blocked Projects navigation.
                    */}
                    <div className="dropdown-toggle-row">
                      <Link
                        href={toCanonicalPath(item.href || '#')}
                        className="dropdown-toggle"
                        onClick={handleLinkClick}
                      >
                        {item.label}
                      </Link>
                      <button
                        type="button"
                        className={`projects-submenu-toggle${isExpanded ? ' is-open' : ''}`}
                        aria-label={
                          isExpanded
                            ? `Collapse ${item.label} submenu`
                            : `Expand ${item.label} submenu`
                        }
                        aria-expanded={isExpanded}
                        aria-controls={`submenu-${item.itemKey || item.id}`}
                        onClick={() => toggleProjectsSubmenu(item.itemKey)}
                      >
                        <span
                          className={`arrow-down projects-chevron${isExpanded ? ' is-open' : ''}`}
                          aria-hidden="true"
                        >
                          ▼
                        </span>
                      </button>
                    </div>
                    <ul
                      id={`submenu-${item.itemKey || item.id}`}
                      className={`dropdown-menu ${isHoverOpen || isExpanded ? 'show' : ''}`}
                    >
                      {item.children.map((child) => (
                        <li key={child.id}>
                          <Link href={toCanonicalPath(child.href || '#')} onClick={handleLinkClick}>
                            {child.label}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </li>
                );
              }

              return (
                <li key={item.id}>
                  <Link href={toCanonicalPath(item.href || '#')} onClick={handleLinkClick}>
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

      </div>
    </nav>
  );
};

export default Navbar;
