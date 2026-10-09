"""Seed CMS tables with the finalized public website content and local AMP images.

Safe to run multiple times:
- Ordered collections match by display_order (updates titles in place)
- Named collections match by title/name/slug
- Unsplash dummy rows are soft-deleted
- Images are copied from frontend assets into backend/uploads

Usage (from backend/ with venv active):
    python scripts/seed_website_content.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import _backend_path  # pylint: disable=unused-import
from app import create_app
from extensions import db
from models.cms_models import (
    FeaturedEvent,
    FooterFocusItem,
    FooterLink,
    FooterSettings,
    HeroBanner,
    HomeEvent,
    HomeGalleryItem,
    HomeProject,
    NavbarItem,
    NavbarSettings,
    PastEvent,
    Testimonial,
    UpcomingEvent,
    utcnow,
)

ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND = ROOT / "frontend"
UPLOADS = ROOT / "backend" / "uploads"

ASSET_COPIES = [
    ("src/assets/hero-education.png", "hero-banners/hero-education.png"),
    ("src/assets/hero-employment.png", "hero-banners/hero-employment.png"),
    ("src/assets/hero-community-impact.png", "hero-banners/hero-community-impact.png"),
    ("src/assets/home-project-etp.png", "home-projects/home-project-etp.png"),
    ("src/assets/home-project-mega-job-fair.png", "home-projects/home-project-mega-job-fair.png"),
    ("src/assets/home-project-career-guidance.png", "home-projects/home-project-career-guidance.png"),
    ("src/assets/home-project-education-support.png", "home-projects/home-project-education-support.png"),
    ("src/assets/gallery/community-registration-drive.png", "home-gallery/community-registration-drive.png"),
    ("src/assets/gallery/community-event-registration.png", "home-gallery/community-event-registration.png"),
    ("src/assets/gallery/amp-ahmedabad-chapter-workshop.png", "home-gallery/amp-ahmedabad-chapter-workshop.png"),
    ("src/assets/gallery/mega-job-fair-byculla-mumbai.png", "home-gallery/mega-job-fair-byculla-mumbai.png"),
    ("src/assets/gallery/mega-job-fair-ballari.png", "home-gallery/mega-job-fair-ballari.png"),
    ("src/assets/gallery/mega-job-fair-thassim-beevi-college.png", "home-gallery/mega-job-fair-thassim-beevi-college.png"),
    ("src/assets/past-events/srinagar-job-fair.jpg", "past-events/srinagar-job-fair.jpg"),
    ("src/assets/past-events/kolkata-job-fair.jpg", "past-events/kolkata-job-fair.jpg"),
    ("src/assets/past-events/doddaballapur-job-fair.jpg", "past-events/doddaballapur-job-fair.jpg"),
    ("src/assets/past-events/nanded-job-fair.jpg", "past-events/nanded-job-fair.jpg"),
    ("src/assets/past-events/nts-2025.jpg", "past-events/nts-2025.jpg"),
    ("src/assets/past-events/mumbai-unity-job-fair-2024.jpg", "past-events/mumbai-unity-job-fair-2024.jpg"),
    ("src/assets/employment-training-workshop.png", "home-events/employment-training-workshop.png"),
    ("src/assets/job-fair-pic-3.png", "home-events/job-fair-pic-3.png"),
    ("public/assets/kupwara-mega-job-fair.jpeg", "home-events/kupwara-mega-job-fair.jpeg"),
    ("public/assets/kupwara-mega-job-fair.jpeg", "featured-events/kupwara-mega-job-fair.jpeg"),
    ("public/assets/kupwara-mega-job-fair.jpeg", "upcoming-events/kupwara-mega-job-fair.jpeg"),
    ("src/assets/medical-relief-camp.png", "upcoming-events/medical-relief-camp.png"),
    ("src/assets/employment-training-workshop.png", "upcoming-events/employment-training-workshop.png"),
    ("src/assets/mentorship-agra-chapter.png", "upcoming-events/mentorship-agra-chapter.png"),
    ("src/assets/gallery/community-registration-drive.png", "upcoming-events/community-registration-drive.png"),
    ("public/assets/testimonials/aamir-malik.png", "testimonials/aamir-malik.png"),
    ("public/assets/testimonials/imran-shaikh.png", "testimonials/imran-shaikh.png"),
    ("public/assets/testimonials/rahul-sharma.png", "testimonials/rahul-sharma.png"),
    ("public/assets/testimonials/imran-siddiqui.png", "testimonials/imran-siddiqui.png"),
    ("public/assets/testimonials/mohammed-arif.png", "testimonials/mohammed-arif.png"),
    ("public/assets/testimonials/mohammed-ekramuddin-shaikh.png", "testimonials/mohammed-ekramuddin-shaikh.png"),
    ("public/images/support-hero-donate.png", "page-settings/support-hero-donate.png"),
    ("public/assets/contact.jpeg", "page-settings/contact.jpeg"),
]


def u(path: str) -> str:
    return f"/uploads/{path}"


def copy_frontend_assets():
    copied = skipped = missing = 0
    for rel_src, rel_dest in ASSET_COPIES:
        src = FRONTEND / rel_src
        dest = UPLOADS / rel_dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            print(f"  missing: {src}")
            missing += 1
            continue
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            skipped += 1
            continue
        shutil.copy2(src, dest)
        copied += 1
    print(f"  Media: {copied} copied, {skipped} unchanged, {missing} missing")


HERO_BANNERS = [
    {
        "title": "Empowering Lives Through",
        "title_accent": "Education",
        "subtitle": (
            "Every child deserves the opportunity to learn, grow and succeed. We support "
            "underprivileged students through scholarships, mentoring, career guidance and "
            "skill development to help them build a brighter future."
        ),
        "image_url": u("hero-banners/hero-education.png"),
        "primary_btn_text": "Learn More",
        "primary_btn_link": "/about",
        "secondary_btn_text": "Our Projects",
        "secondary_btn_link": "/projects",
        "display_order": 1,
    },
    {
        "title": "Creating Opportunities Through",
        "title_accent": "Employment",
        "subtitle": (
            "A good job can transform a family's future. Through employability training, "
            "career guidance, job fairs and placement support, we help young people become "
            "job-ready and connect them with meaningful employment opportunities."
        ),
        "image_url": u("hero-banners/hero-employment.png"),
        "primary_btn_text": "Join Us",
        "primary_btn_link": "/volunteer",
        "secondary_btn_text": "Our Impact",
        "secondary_btn_link": "/#impact",
        "display_order": 2,
    },
    {
        "title": "Building Stronger",
        "title_accent": "Communities",
        "subtitle": (
            "We empower individuals and families through skill development, entrepreneurship "
            "support, healthcare initiatives and community development programs, enabling them "
            "to become self-reliant and lead dignified lives."
        ),
        "image_url": u("hero-banners/hero-community-impact.png"),
        "primary_btn_text": "Support Us",
        "primary_btn_link": "/support-us",
        "secondary_btn_text": "Our Mission",
        "secondary_btn_link": "/what-we-do",
        "display_order": 3,
    },
]

HOME_PROJECTS = [
    {"title": "Employability Training Program (ETP)", "image_url": u("home-projects/home-project-etp.png"), "display_order": 1},
    {"title": "Mega Job Fair", "image_url": u("home-projects/home-project-mega-job-fair.png"), "display_order": 2},
    {"title": "Career Guidance & Mentorship", "image_url": u("home-projects/home-project-career-guidance.png"), "display_order": 3},
    {"title": "Education Support", "image_url": u("home-projects/home-project-education-support.png"), "display_order": 4},
]

HOME_GALLERY = [
    {
        "image_url": u("home-gallery/community-registration-drive.png"),
        "alt_text": "Large outdoor crowd queued for a community registration and outreach drive",
        "title": "Youth Outreach & Employment Drive",
        "description": "A massive turnout of community members gathering for an organized event, showcasing large-scale engagement.",
        "display_order": 1,
    },
    {
        "image_url": u("home-gallery/community-event-registration.png"),
        "alt_text": "Organizers assisting participants with registration at a community event desk",
        "title": "Guidance & Mentoring of Youth",
        "description": "Local residents receive guidance and register for essential services at a dedicated event hub.",
        "display_order": 2,
    },
    {
        "image_url": u("home-gallery/amp-ahmedabad-chapter-workshop.png"),
        "alt_text": "Presenter leading an AMP Ahmedabad Chapter workshop for seated members",
        "title": "Skill Development Program",
        "description": "Members attend a professional development workshop focused on community initiatives.",
        "display_order": 3,
    },
    {
        "image_url": u("home-gallery/mega-job-fair-byculla-mumbai.png"),
        "alt_text": "Speaker at the podium during the Mega Job Fair at Byculla, Mumbai",
        "title": "Mega Job Fair at Byculla, Mumbai",
        "description": "Dignitaries and speakers at the Mega Job Fair held at Saboo Siddik College, Mumbai.",
        "display_order": 4,
    },
    {
        "image_url": u("home-gallery/mega-job-fair-ballari.png"),
        "alt_text": "Audience seated under a tent at the Mega Job Fair in Ballari, Karnataka",
        "title": "Mega Job Fair — Ballari, Karnataka",
        "description": "A large-scale recruitment event where hundreds of candidates gathered to meet employers.",
        "display_order": 5,
    },
    {
        "image_url": u("home-gallery/mega-job-fair-thassim-beevi-college.png"),
        "alt_text": "Interview stations filled with candidates at a Mega Job Fair college auditorium",
        "title": "Mega Job Fair at Chennai, Tamil Nadu",
        "description": "Interview stations and attendees engaged in career opportunities at the college auditorium.",
        "display_order": 6,
    },
]

HOME_EVENTS = [
    {
        "title": "Kupwara Mega Job Fair",
        "description": "A Mega Job Fair connecting job seekers with employers across multiple industries and creating opportunities for meaningful employment.",
        "speaker": "",
        "event_date": "22 August 2026",
        "venue": "Kupwara, Jammu & Kashmir",
        "image_url": u("home-events/kupwara-mega-job-fair.jpeg"),
        "registration_link": "/events",
        "button_text": "View Details",
        "display_order": 1,
    },
    {
        "title": "Employability Training Programme (ETP)",
        "description": "A practical training programme that prepares graduates for today's job market through resume writing, communication skills and interview preparation.",
        "speaker": "",
        "event_date": "20 September 2026",
        "venue": "Mumbai",
        "image_url": u("home-events/employment-training-workshop.png"),
        "registration_link": "/events",
        "button_text": "View Details",
        "display_order": 2,
    },
    {
        "title": "Free Medical Camp & Health Screening",
        "description": "Providing free health check-ups, critical illness screenings, and medical relief support for underserved communities.",
        "speaker": "",
        "event_date": "22 August 2026",
        "venue": "Hyderabad",
        "image_url": u("upcoming-events/medical-relief-camp.png"),
        "registration_link": "/events",
        "button_text": "View Details",
        "display_order": 3,
    },
]

TESTIMONIALS = [
    {
        "name": "Mrinal Kanti Debnath",
        "designation": "HR Recruiter, Godrej Appliances",
        "location": "",
        "profile_image": u("testimonials/aamir-malik.png"),
        "message": "We have been associated with AMP India Foundation's employment initiatives for several years. Their job fairs are well-organized and help us connect with quality candidates. We look forward to continuing this valuable partnership in the years ahead.",
        "rating": 5,
        "display_order": 1,
    },
    {
        "name": "Yawar Ihsan",
        "designation": "Operations Officer, G4S Secure",
        "location": "",
        "profile_image": u("testimonials/imran-shaikh.png"),
        "message": "Participating in the employment drive was a rewarding experience. It gave me the opportunity to interact with talented candidates from diverse backgrounds while witnessing the Foundation's commitment to creating meaningful career opportunities for job seekers.",
        "rating": 5,
        "display_order": 2,
    },
    {
        "name": "Chandrakant Khade",
        "designation": "Apprentice Recruitment Officer, Allied Resource Management Services Pvt. Ltd.",
        "location": "",
        "profile_image": u("testimonials/rahul-sharma.png"),
        "message": "It was a wonderful experience participating in the event. The programme was professionally managed and provided an excellent platform for connecting deserving candidates with employment opportunities.",
        "rating": 5,
        "display_order": 3,
    },
    {
        "name": "Mohammed Farrok Gheewala",
        "designation": "Chairman, F. Gheewala HR Consultants",
        "location": "",
        "profile_image": u("testimonials/imran-siddiqui.png"),
        "message": "The Mumbai Job Fair was a well-coordinated initiative, and we appreciate the dedication and professionalism of the AMP India Foundation team. We value our association and look forward to participating in many more such impactful programmes.",
        "rating": 5,
        "display_order": 4,
    },
    {
        "name": "Vikram Singh",
        "designation": "Lead Recruiter, PVK HR Solutions Pvt. Ltd.",
        "location": "",
        "profile_image": u("testimonials/mohammed-arif.png"),
        "message": "AMP India Foundation is creating meaningful social impact by connecting underprivileged youth with employment opportunities. Their commitment, transparency and nationwide outreach make them a trusted partner in community development.",
        "rating": 5,
        "display_order": 5,
    },
    {
        "name": "Mohammed Ekramuddin Shaikh",
        "designation": "Co-Founder & Managing Partner, Nutra Essenza Wellness LLP",
        "location": "",
        "profile_image": u("testimonials/mohammed-ekramuddin-shaikh.png"),
        "message": "My association with AMP India Foundation's Employment Assistance Cell has been truly inspiring. Their dedication to career guidance, mentoring and skill development is empowering thousands of young people and helping build a stronger and more confident society.",
        "rating": 5,
        "display_order": 6,
    },
]

FEATURED_EVENTS = [
    {
        "title": "Kupwara Mega Job Fair",
        "event_date": "22 August 2026",
        "event_time": "",
        "venue": "Kupwara, Jammu & Kashmir",
        "category": "Employment",
        "description": "A Mega Job Fair connecting job seekers with employers across multiple industries and creating opportunities for meaningful employment.",
        "banner_image": u("featured-events/kupwara-mega-job-fair.jpeg"),
        "display_order": 1,
    },
]

UPCOMING_EVENTS = [
    {
        "title": "Kupwara Mega Job Fair",
        "category": "Employment",
        "event_date": "22 August 2026",
        "venue": "Kupwara, Jammu & Kashmir",
        "description": "A Mega Job Fair connecting job seekers with employers across multiple industries and creating opportunities for meaningful employment.",
        "image_url": u("upcoming-events/kupwara-mega-job-fair.jpeg"),
        "display_order": 1,
    },
    {
        "title": "Free Medical Camp & Health Screening",
        "category": "Medical Camp",
        "event_date": "22 Aug 2026",
        "venue": "Hyderabad",
        "description": "Providing free health check-ups, critical illness screenings, and medical relief support for underserved communities.",
        "image_url": u("upcoming-events/medical-relief-camp.png"),
        "display_order": 2,
    },
    {
        "title": "Vocational Skill Development Bootcamp",
        "category": "Skill Development",
        "event_date": "05 Sep 2026",
        "venue": "Bengaluru",
        "description": "Intensive vocational training in digital skills, tailoring, and small-scale entrepreneurship for sustainable livelihoods.",
        "image_url": u("upcoming-events/employment-training-workshop.png"),
        "display_order": 3,
    },
    {
        "title": "Student Mentorship & Career Guidance Summit",
        "category": "Career Guidance",
        "event_date": "14 Oct 2026",
        "venue": "Pune",
        "description": "One-on-one mentoring sessions with industry professionals to guide students through academic and career decision-making.",
        "image_url": u("upcoming-events/mentorship-agra-chapter.png"),
        "display_order": 4,
    },
    {
        "title": "Community Outreach & Upliftment Drive",
        "category": "Community Outreach",
        "event_date": "12 Dec 2026",
        "venue": "Kolkata",
        "description": "Grassroots community development initiative distributing essential supplies, financial literacy workshops, and self-help group setups.",
        "image_url": u("upcoming-events/community-registration-drive.png"),
        "display_order": 5,
    },
]

GALLERY_ITEMS = [
    {
        "title": "AMP's 2nd Srinagar, Kashmir Job Fair",
        "event_date": "30 August 2025",
        "venue": "Srinagar, Jammu & Kashmir",
        "image_url": u("past-events/srinagar-job-fair.jpg"),
        "category": "Employment",
        "description": "AMP, in partnership with Hamdard Learning & Welfare Society, organised a mega Job Fair at IITM campus, Hyderpora, Srinagar. The event registered 2,769 candidates, with 1,606 interviewed and 404 candidates shortlisted and selected.",
        "display_order": 1,
    },
    {
        "title": "AMP Kolkata Job Fair",
        "event_date": "23 August 2025",
        "venue": "Kolkata, West Bengal",
        "image_url": u("past-events/kolkata-job-fair.jpg"),
        "category": "Employment",
        "description": "AMP, in partnership with Govt. Girls' General Degree College, organised a Job Fair in Kolkata with 492 registered candidates and 18 participating companies offering 2,800+ job vacancies. 288 candidates were shortlisted and selected.",
        "display_order": 2,
    },
    {
        "title": "AMP Mega Job Fair in Doddaballapur",
        "event_date": "12 April 2025",
        "venue": "Doddaballapur, Karnataka",
        "image_url": u("past-events/doddaballapur-job-fair.jpg"),
        "category": "Employment",
        "description": "AMP organised a Mega Job Fair at Lavanya Degree College, Doddaballapur, in partnership with Lavanya Group of Institutions. The event attracted 215 candidates, with 9 companies offering 1,972+ vacancies and 113 candidates shortlisted and selected.",
        "display_order": 3,
    },
    {
        "title": "AMP Mega Job Fair in Nanded",
        "event_date": "11 January 2025",
        "venue": "Nanded, Maharashtra",
        "image_url": u("past-events/nanded-job-fair.jpg"),
        "category": "Employment",
        "description": "AMP, in association with World Memon Organisation and Memon Community Trust, organised a Mega Job Fair at ITM College, Nanded. Around 1,000 candidates were interviewed, with 450+ selected and shortlisted and 33 corporates and recruiters participating.",
        "display_order": 4,
    },
    {
        "title": "AMP National Talent Search 2025 – Grand Launch",
        "event_date": "7 December 2024",
        "venue": "Pan India",
        "image_url": u("past-events/nts-2025.jpg"),
        "category": "Education",
        "description": "AIF/AMP launched the National Talent Search 2025 programme and felicitated the National Awardees, bringing together distinguished guests, professionals and community leaders to celebrate talent, education and achievement.",
        "display_order": 5,
    },
    {
        "title": "AMP Unity Job Fair at Mumbai 2024",
        "event_date": "17 August 2024",
        "venue": "Mumbai, Maharashtra",
        "image_url": u("past-events/mumbai-unity-job-fair-2024.jpg"),
        "category": "Employment",
        "description": "AMP, along with Pir Makhdum Saheb Charitable Trust and Bombay Catholic Sabha, organised a Free Mega Job Fair at Sacred Heart Boys School, Santacruz, Mumbai. The event had 1,768 candidates interviewed, with 80 selected and 554 shortlisted for the next round.",
        "display_order": 6,
    },
]

HOME_PREVIEW = [
    {
        "title": "Education Support",
        "subtitle": "Building Brighter Futures",
        "description": "We help deserving students continue their education through scholarships, mentoring, career guidance and skill development, ensuring that financial hardship does not become a barrier to success.",
        "href": "/projects/education",
        "image_url": u("home-preview-cards/education-support-students.png"),
        "display_order": 1,
    },
    {
        "title": "Employment Support",
        "subtitle": "Creating Better Career Opportunities",
        "description": "We prepare young people for successful careers through employability training, career counselling, job fairs and placement support, helping them secure meaningful employment.",
        "href": "/projects/employment",
        "image_url": u("home-preview-cards/employment-support-job-fair.jpg"),
        "display_order": 2,
    },
    {
        "title": "Mentorship & Guidance",
        "subtitle": "Inspiring the Next Generation",
        "description": "Our experienced professionals mentor students and young graduates by sharing knowledge, career advice and life skills that help them achieve their personal and professional goals.",
        "href": "/projects/mentorship",
        "image_url": u("home-preview-cards/career-guidance-seminar.png"),
        "display_order": 3,
    },
]

IMPACT_STATS = [
    {"title": "CANDIDATES PLACED", "target_value": 100000, "suffix": "+", "icon_key": "users", "display_order": 1},
    {"title": "JOB DRIVES ORGANISED", "target_value": 625, "suffix": "+", "icon_key": "briefcase", "display_order": 2},
    {"title": "EMPLOYABILITY TRAINING PROGRAMMES", "target_value": 350, "suffix": "+", "icon_key": "graduation", "display_order": 3},
    {"title": "MEGA JOB FAIRS CONDUCTED", "target_value": 110, "suffix": "+", "icon_key": "network", "display_order": 4},
]

PROJECT_CARDS = [
    {
        "slug": "education",
        "title": "Education",
        "subtitle": "Building Brighter Futures",
        "href": "/projects/education",
        "image_url": u("project-cards/amp-ahmedabad-chapter-workshop.png"),
        "initiatives": "Scholarships for deserving students\nCareer Guidance Programmes\nStudent Mentorship\nEducational Support\nCentres of Excellence",
        "display_order": 1,
    },
    {
        "slug": "employment",
        "title": "Employment Assistance",
        "subtitle": "Connecting Talent with Opportunity",
        "href": "/projects/employment",
        "image_url": u("project-cards/job-fair-pic-3.png"),
        "initiatives": "Employability Training Programmes (ETP)\nCareer Counselling\nMega Job Fairs\nPlacement Support\nCampus Recruitment Drives",
        "display_order": 2,
    },
    {
        "slug": "skill-development",
        "title": "Skill Development",
        "subtitle": "Learning Skills for a Better Tomorrow",
        "href": "/projects/training",
        "image_url": u("project-cards/employment-training-workshop.png"),
        "initiatives": "Vocational Training\nTechnical Skills Development\nEntrepreneurship Training\nDigital Skills\nLivelihood Programmes",
        "display_order": 3,
    },
    {
        "slug": "medical",
        "title": "Medical Relief",
        "subtitle": "Caring for Health. Supporting Lives.",
        "href": "/projects/medical",
        "image_url": u("project-cards/medical-relief-camp.png"),
        "initiatives": "Free Medical Camps\nHealth Awareness Programmes\nEmergency Medical Assistance\nMedical Aid for Needy Patients",
        "display_order": 4,
    },
    {
        "slug": "empowerment",
        "title": "Economic Empowerment",
        "subtitle": "Strengthening Families and Communities",
        "href": "/projects/empowerment",
        "image_url": u("project-cards/economic-empowerment-tailoring.png"),
        "initiatives": "Livelihood Support\nEntrepreneurship Promotion\nFinancial Awareness\nCommunity Development Programmes\nWomen & Youth Empowerment",
        "display_order": 5,
    },
    {
        "slug": "mentorship",
        "title": "Mentorship",
        "subtitle": "Guiding the Leaders of Tomorrow",
        "href": "/projects/mentorship",
        "image_url": u("project-cards/mentorship-agra-chapter.png"),
        "initiatives": "One-to-One Mentoring\nCareer Guidance\nLeadership Development\nProfessional Networking\nSoft Skills Training",
        "display_order": 6,
    },
]

PROJECT_PAGES = [
    {
        "slug": "education",
        "title": "EDUCATION",
        "subtitle": "SKILL DEVELOPMENT & LIVELIHOOD LIFTS",
        "quote": "Empowering BPL youth through localized technical skill frameworks.",
        "badge": "NSDC COMPLIANT",
        "image_url": u("project-pages/education-project-seminar.png"),
        "paragraph_1": "Indian youth from the lower-strata of society, especially from BPL families, are unable to continue their education after the Primary section as they must support their families to make ends meet. Consequently, they resort to menial jobs that yield minimal earnings and lock them into structural poverty circles.",
        "paragraph_2": "AIF conducts targeted vocational training for these school dropouts, focusing on easy-to-learn, market-driven technical skills like Mobile Repairing, Air-Conditioning & Refrigerator Maintenance, Water Filter Repairing, and Motor Vehicle Servicing.",
        "paragraph_3": "Through strategic tie-ups with NSDC-sponsored CSR programmes, AIF delivers free, short-term vocational skills training models nationwide, opening secure employment pipelines and self-sustaining entrepreneurial opportunities.",
        "display_order": 1,
    },
    {
        "slug": "employment",
        "title": "SUPPORT",
        "subtitle": "CAREER PLACEMENT INFRASTRUCTURE",
        "quote": "Bridging the transition from student networks to corporate ecosystems.",
        "badge": "PLACEMENT READY",
        "image_url": u("project-pages/employment-project-job-fair.png"),
        "paragraph_1": "Securing meaningful jobs with adequate compensation is a consistent struggle for the vast majority of the Indian working class, especially with an expanding educated demographic entering the market annually.",
        "paragraph_2": "Because traditional academic paths do not place sufficient importance on practical soft-skills and modern corporate grooming, AIF works closely to bridge this transition gap and create market-ready candidates.",
        "paragraph_3": "We actively host soft-skills development workshops, intensive employability seminars, and large-scale Job Drives and Fairs across the country to connect talented youth with localized corporate career avenues.",
        "display_order": 2,
    },
    {
        "slug": "training",
        "title": "TRAINING",
        "subtitle": "CORPORATE GROOMING & PREPARATION",
        "quote": "Polishing core foundational skills to ensure immediate employment fit.",
        "badge": "ETP ADVANCED",
        "image_url": u("project-pages/employment-training-workshop.png"),
        "paragraph_1": "AIF conducts the Employability Training Program (ETP) to train youngsters in crucial pre-employment preparation, assisting job seekers in finding the right opportunity, at the right time and place.",
        "paragraph_2": "Spearheaded by corporate trainers, ETP focuses on critical professional metrics including target job hunting strategies, effective resume structuring, interview performance management, professional grooming, and communications.",
        "paragraph_3": "",
        "display_order": 3,
    },
    {
        "slug": "medical",
        "title": "MEDICAL AID",
        "subtitle": "HEALTHCARE INTERVENTION & OUTREACH",
        "quote": "Breaking barriers to provide essential diagnostic and clinical relief.",
        "badge": "CRITICAL HEALTH",
        "image_url": u("project-pages/medical-relief-camp.png"),
        "paragraph_1": "Uplifting the underserved and vulnerable through critical medical relief frameworks, bringing timely aid to individuals without any bias of Caste, Community, Creed, or Religion.",
        "paragraph_2": "AIF coordinates responsive healthcare networks and positive medical interventions to manage diagnostic camps, establish free essential medicine distribution clinics, and offer immediate emergency financial workflows for critical tertiary care.",
        "paragraph_3": "",
        "display_order": 4,
    },
    {
        "slug": "empowerment",
        "title": "EMPOWERMENT",
        "subtitle": "FINANCIAL INDEPENDENCE SYSTEM",
        "quote": "Cultivating entrepreneurial self-reliance across urban and rural chapters.",
        "badge": "SUSTAINABLE CAPITAL",
        "image_url": u("project-pages/economic-empowerment-tailoring.png"),
        "paragraph_1": "AIF builds dedicated, voluntary social platforms that target sustainable, long-term self-sufficiency through structured regional livelihood assistance programs.",
        "paragraph_2": "By opening access to early capital guidance, small enterprise management tools, and direct marketplace connection assistance, we empower vulnerable demographics to successfully establish independent livelihoods.",
        "paragraph_3": "",
        "display_order": 5,
    },
    {
        "slug": "mentorship",
        "title": "MENTORSHIP",
        "subtitle": "INTELLECTUAL GUIDANCE FRAMEWORK",
        "quote": "Connecting industry experience with first-generation student networks.",
        "badge": "MENTOR NETWORK",
        "image_url": u("project-pages/mentorship-agra-chapter.png"),
        "paragraph_1": "Making a real, structural difference to the student community by utilizing the shared knowledge, intellect, professional experience, and competencies of established corporate professionals.",
        "paragraph_2": "Our core focus targets the comprehensive educational development of the community—particularly its weakest sections—fostering an environment where every student has an equal stake in regional and national growth.",
        "paragraph_3": "",
        "display_order": 6,
    },
]

ABOUT_FOCUS = [
    {"title": "Education", "description": "Supporting deserving students through scholarships, career guidance, mentoring, digital learning and skill development to help them achieve their educational goals.", "display_order": 1},
    {"title": "Employment", "description": "Preparing youth for successful careers through employability training, job fairs, placement support and industry partnerships.", "display_order": 2},
    {"title": "Skill Development", "description": "Providing vocational and technical training that improves employability and creates opportunities for self-employment.", "display_order": 3},
    {"title": "Healthcare", "description": "Extending medical assistance, health awareness programmes, medical camps and emergency support to individuals and families in need.", "display_order": 4},
    {"title": "Empowerment", "description": "Promoting sustainable livelihoods, financial inclusion, entrepreneurship and social development initiatives that strengthen communities.", "display_order": 5},
]

ABOUT_VALUES = [
    {"title": "Compassion", "description": "We serve every individual with empathy, dignity and respect.", "icon_key": "shield", "display_order": 1},
    {"title": "Integrity", "description": "We maintain the highest standards of honesty, transparency and accountability in everything we do.", "icon_key": "users", "display_order": 2},
    {"title": "Excellence", "description": "We continuously strive to deliver impactful programmes with professionalism and quality.", "icon_key": "award", "display_order": 3},
]

ABOUT_OBJECTIVES = [
    {"number_label": "01", "title": "Education & Scholarships", "description": "Helping deserving students continue their education through scholarships, educational support, mentoring and career guidance.", "highlighted": "no", "display_order": 1},
    {"number_label": "02", "title": "Employability & Career Development", "description": "Organising employability training programmes, career counselling sessions, job drives and Mega Job Fairs to connect youth with employment opportunities.", "highlighted": "yes", "display_order": 2},
    {"number_label": "03", "title": "Skill Development", "description": "Providing vocational and technical training that prepares individuals for today's job market and encourages entrepreneurship.", "highlighted": "no", "display_order": 3},
    {"number_label": "04", "title": "Healthcare & Medical Support", "description": "Supporting health camps, emergency medical assistance and healthcare initiatives for underprivileged individuals and families.", "highlighted": "yes", "display_order": 4},
    {"number_label": "05", "title": "Community Development", "description": "Implementing programmes that promote self-reliance, financial empowerment and the overall well-being of underserved communities.", "highlighted": "no", "display_order": 5},
]

ABOUT_FAQS = [
    {"title": "What does AMP India Foundation do?", "description": "AMP India Foundation works in the areas of education, employment, skill development, healthcare and community empowerment to improve the lives of underprivileged individuals across India.", "display_order": 1},
    {"title": "Who can benefit from your programmes?", "description": "Students, job seekers, women, youth, families and disadvantaged communities from across India can benefit from our various initiatives, subject to the eligibility criteria of each programme.", "display_order": 2},
    {"title": "How can I support the Foundation?", "description": "You can support our mission by making a donation, volunteering your time and skills, mentoring students, partnering with us, or helping spread awareness about our work.", "display_order": 3},
    {"title": "Can I volunteer with AMP India Foundation?", "description": "Yes. We welcome students, professionals, entrepreneurs and retirees who wish to contribute their time, expertise and experience towards social development.", "display_order": 4},
    {"title": "Are your programmes open to everyone?", "description": "Yes. Our initiatives are implemented without discrimination based on caste, community, creed, gender or religion.", "display_order": 5},
]

EVENTS_TIMELINE = [
    {"period": "January – March", "title": "Education and Career Guidance Programmes", "display_order": 1},
    {"period": "April – June", "title": "Employability Training and Skill Development", "display_order": 2},
    {"period": "July – September", "title": "Mega Job Fairs, Medical Camps and Community Outreach", "display_order": 3},
    {"period": "October – December", "title": "Mentorship Programmes, Volunteer Engagement and Social Development Initiatives", "display_order": 4},
]

EVENTS_CATEGORIES = [
    {"title": "Education", "description": "Scholarships, educational workshops and career guidance programmes.", "icon_key": "graduation", "display_order": 1},
    {"title": "Employment", "description": "Employability training, job fairs, placement drives and recruitment events.", "icon_key": "briefcase", "display_order": 2},
    {"title": "Healthcare", "description": "Medical camps, health awareness initiatives and medical assistance.", "icon_key": "heart", "display_order": 3},
    {"title": "Skill Development", "description": "Vocational training, entrepreneurship workshops and livelihood programmes.", "icon_key": "wrench", "display_order": 4},
    {"title": "Mentorship", "description": "Career counselling, leadership development and professional mentoring.", "icon_key": "users", "display_order": 5},
    {"title": "Community Development", "description": "Outreach programmes that strengthen families and communities through sustainable support.", "icon_key": "hands", "display_order": 6},
]

NAVBAR_ITEMS = [
    {"label": "HOME", "href": "/home", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 1},
    {"label": "ABOUT US", "href": "/about", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 2},
    {"label": "PROJECTS", "href": "/projects/education", "item_type": "dropdown", "item_key": "projects", "parent_key": None, "display_order": 3},
    {"label": "Education", "href": "/projects/education", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 4},
    {"label": "Medical Relief", "href": "/projects/medical", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 5},
    {"label": "Employment Support", "href": "/projects/employment", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 6},
    {"label": "Economic Empowerment", "href": "/projects/empowerment", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 7},
    {"label": "Student Mentorship", "href": "/projects/mentorship", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 8},
    {"label": "Employment Training", "href": "/projects/training", "item_type": "link", "item_key": None, "parent_key": "projects", "display_order": 9},
    {"label": "EVENTS", "href": "/events", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 10},
    {"label": "VOLUNTEER", "href": "/volunteer", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 11},
    {"label": "SUPPORT US", "href": "/support-us", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 12},
    {"label": "CONTACT", "href": "/contact", "item_type": "link", "item_key": None, "parent_key": None, "display_order": 13},
]

FOOTER_LINKS = [
    {"label": "Home", "href": "/", "display_order": 1},
    {"label": "About Us", "href": "/about", "display_order": 2},
    {"label": "What We Do", "href": "/what-we-do", "display_order": 3},
    {"label": "Projects", "href": "/projects", "display_order": 4},
    {"label": "Events", "href": "/events", "display_order": 5},
    {"label": "Join Us / Volunteer", "href": "/volunteer", "display_order": 6},
    {"label": "Support Us", "href": "/support-us", "display_order": 7},
    {"label": "Contact", "href": "/contact", "display_order": 8},
    {"label": "Terms & Conditions", "href": "/terms-and-conditions", "display_order": 9},
    {"label": "Privacy Policy", "href": "/privacy-policy", "display_order": 10},
    {"label": "Refund Policy", "href": "/refund-policy", "display_order": 11},
]

FOOTER_FOCUS = [
    {"title": "National Talent Search Examination", "href": "/projects/education", "date_label": "July 2026", "display_order": 1},
    {"title": "Employability Training Programs", "href": "/projects/training", "date_label": "June 2026", "display_order": 2},
    {"title": "Higher Education Scholarship Distribution", "href": "/projects/education", "date_label": "May 2026", "display_order": 3},
]

FOOTER_SETTINGS = {
    "cta_heading": "Join Our Mission to Empower Lives Through Education & Employment.",
    "cta_button_text": "BECOME A VOLUNTEER",
    "cta_button_link": "/volunteer",
    "about_heading": "ABOUT US",
    "about_text": (
        "AMP India Foundation is a non-profit organization dedicated to regularise "
        "and scale up socio-economic development welfare activities. We empower "
        "underprivileged youth through sustainable educational models, rigorous training, "
        "and professional mentorship."
    ),
    "about_link_text": "READ MORE →",
    "about_link_href": "/about",
    "useful_links_heading": "USEFUL LINKS",
    "recent_focus_heading": "RECENT FOCUS",
    "contact_heading": "GET IN TOUCH",
    "address_label": "Address:",
    "address_text": "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008",
    "phone_label": "Phone:",
    "phone_text": "+91 8291101312",
    "email_label": "Email:",
    "email_text": "contact@ampindiafoundation.org",
    "follow_heading": "FOLLOW US",
    "facebook_url": "https://www.facebook.com/ampindiafoundation/",
    "instagram_url": "https://www.instagram.com/ampindiafoundation/",
    "copyright_text": "Copyrights © 2026 All Rights Reserved. Powered by ",
    "copyright_highlight": "AMP India Foundation",
}

PAGE_SETTINGS = {
    "about": {
        "hero_image_url": u("page-settings/about-hero.png"),
        "secondary_image_url": u("page-settings/about-opportunity-seminar.png"),
        "tertiary_image_url": u("page-settings/about-opportunity-career-chart.png"),
        "title": "Empowering Lives.",
        "title_accent": "Transforming Communities.",
        "subtitle": "At AMP India Foundation, we believe that every individual deserves an opportunity to learn, earn and live with dignity. Through education, employment, healthcare, skill development and community empowerment, we work to create lasting change for underprivileged communities across India.",
        "body": "AMP India Foundation (AIF) is a registered non-profit organization committed to empowering underprivileged individuals and communities through sustainable development initiatives.",
        "extra": {
            "story_paragraph": "Established by a network of committed professionals and social leaders, AIF works across India to improve access to quality education, meaningful employment, healthcare, skill development and economic opportunities.",
            "vision": "To build an inclusive India where every individual has equal opportunities to learn, earn and live with dignity.",
            "mission": "To empower underprivileged communities through education, employment, healthcare, skill development, mentorship and sustainable livelihood initiatives by connecting professionals, volunteers, donors and institutions.",
        },
    },
    "events": {
        "hero_image_url": u("page-settings/events-hero.png"),
        "badge": "AMP India Foundation Events",
        "title": "Creating Opportunities.",
        "title_accent": "Inspiring Change.",
        "subtitle": "Every event at AMP India Foundation is a step towards building stronger communities. From career guidance and job fairs to health camps and skill development workshops, our events create opportunities that transform lives.",
        "cta_text": "Explore Upcoming Events",
        "cta_link": "#upcoming-events",
        "extra": {
            "volunteer_title": "Be Part of Our Next Event",
            "volunteer_text": "Whether you are a student, volunteer, professional, institution or corporate partner, your participation helps create opportunities that transform lives. Together, we can make every event a step towards a stronger and more inclusive society.",
        },
    },
    "support": {
        "hero_image_url": u("page-settings/support-hero-donate.png"),
        "secondary_image_url": u("page-settings/hero-community-impact.png"),
        "badge": "SUPPORT US",
        "title": "Your Support Can",
        "title_accent": "Change a Life",
        "subtitle": "Every contribution, big or small, helps create opportunities for education, employment, healthcare and community development. Together, we can empower individuals, strengthen families and build a brighter future for thousands across India.",
        "quote": "Behind every scholarship is a student's dream. Behind every job is a family's hope. Behind every volunteer is a community made stronger.",
        "cta_text": "TOGETHER FOR CHANGE",
        "extra": {
            "account_name": "AMP India Foundation",
            "bank": "Kotak Mahindra Bank",
            "account_number": "3114476665",
            "account_type": "Savings Account",
            "ifsc": "KKBK0001348",
        },
    },
    "contact": {
        "hero_image_url": u("page-settings/contact.jpeg"),
        "title": "Let's start a",
        "title_accent": "meaningful",
        "subtitle": "We would love to hear from you. Reach out for programmes, partnerships, volunteering or support.",
        "extra": {
            "address": "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008",
            "phone": "+91 8291101312",
            "email": "contact@ampindiafoundation.org",
        },
    },
    "projects": {
        "hero_image_url": u("page-settings/employment-support-job-fair.jpg"),
        "badge": "OUR PROJECTS",
        "title": "Creating Opportunities That Last",
        "subtitle": "From classrooms to careers, our programmes help people learn, earn and live with dignity.",
    },
    "home-welcome": {
        "title": "WELCOME TO",
        "title_accent": "AMP INDIA FOUNDATION",
        "subtitle": "Together, We Create Lasting Change",
        "body": "AMP India Foundation (AIF) is a registered non-profit organization working to improve the lives of underprivileged communities across India. Through education, employment, skill development, healthcare and community empowerment, we help people build better futures with dignity and confidence.",
        "extra": {
            "paragraph": "Supported by a nationwide network of professionals, volunteers, donors and partner organizations, we strive to create opportunities that bring lasting social impact.",
        },
    },
    "home-impact": {
        "hero_image_url": u("hero-banners/hero-community-impact.png"),
        "title": "Our Impact",
    },
}


def upsert(model, match_filters: dict, payload: dict) -> str:
    payload = {**payload, "status": "published"}
    row = model.query.filter_by(**match_filters).first()
    if row:
        for key, value in payload.items():
            setattr(row, key, value)
        if hasattr(row, "is_deleted"):
            row.is_deleted = False
            row.deleted_at = None
        return "updated"
    db.session.add(model(**payload))
    return "created"


def seed_ordered(label, model, items):
    created = updated = 0
    for item in items:
        filters = {"display_order": item["display_order"]}
        if hasattr(model, "is_deleted"):
            row = model.query.filter_by(display_order=item["display_order"], is_deleted=False).first()
            payload = {**item, "status": "published"}
            if row:
                for key, value in payload.items():
                    setattr(row, key, value)
                updated += 1
            else:
                db.session.add(model(**payload))
                created += 1
        else:
            action = upsert(model, filters, item)
            created += int(action == "created")
            updated += int(action == "updated")
    print(f"  {label}: {created} created, {updated} updated ({len(items)} total)")


def seed_collection(label, model, items, match_key: str):
    created = updated = 0
    for item in items:
        action = upsert(model, {match_key: item[match_key]}, item)
        created += int(action == "created")
        updated += int(action == "updated")
    print(f"  {label}: {created} created, {updated} updated ({len(items)} total)")


def retire_unsplash(model, image_fields):
    count = 0
    for row in model.query.filter_by(is_deleted=False).all():
        for field in image_fields:
            url = getattr(row, field, "") or ""
            if "unsplash.com" in url.lower():
                row.is_deleted = True
                row.deleted_at = utcnow()
                count += 1
                break
    if count:
        print(f"  Retired {count} Unsplash {model.__tablename__} row(s)")


def retire_names_not_in(model, attr, keep):
    count = 0
    keep_set = set(keep)
    for row in model.query.filter_by(is_deleted=False).all():
        if getattr(row, attr) not in keep_set:
            row.is_deleted = True
            row.deleted_at = utcnow()
            count += 1
    if count:
        print(f"  Retired {count} obsolete {model.__tablename__} row(s)")


def seed_navbar_settings():
    row = NavbarSettings.query.order_by(NavbarSettings.id.asc()).first()
    payload = {"logo_url": "/assets/logo.png", "logo_alt": "AMP Logo", "logo_link": "/"}
    if row:
        for key, value in payload.items():
            setattr(row, key, value)
        print("  Navbar settings: updated")
    else:
        db.session.add(NavbarSettings(**payload, created_at=utcnow(), updated_at=utcnow()))
        print("  Navbar settings: created")


def seed_footer_settings():
    row = FooterSettings.query.order_by(FooterSettings.id.asc()).first()
    if row:
        for key, value in FOOTER_SETTINGS.items():
            setattr(row, key, value)
        print("  Footer settings: updated")
    else:
        db.session.add(FooterSettings(**FOOTER_SETTINGS, created_at=utcnow(), updated_at=utcnow()))
        print("  Footer settings: created")


def seed_navbar_items():
    created = updated = 0
    for item in NAVBAR_ITEMS:
        filters = {"label": item["label"], "href": item["href"], "parent_key": item.get("parent_key")}
        action = upsert(NavbarItem, filters, item)
        created += int(action == "created")
        updated += int(action == "updated")
    print(f"  Navbar items: {created} created, {updated} updated ({len(NAVBAR_ITEMS)} total)")


def main():
    app = create_app()
    with app.app_context():
        print("Copying finalized frontend images into /uploads…")
        copy_frontend_assets()
        print("Seeding website content into MySQL…")
        seed_ordered("Hero banners", HeroBanner, HERO_BANNERS)
        seed_ordered("Home projects", HomeProject, HOME_PROJECTS)
        seed_ordered("Home gallery", HomeGalleryItem, HOME_GALLERY)
        seed_ordered("Home events", HomeEvent, HOME_EVENTS)
        seed_collection("Testimonials", Testimonial, TESTIMONIALS, "name")
        seed_ordered("Featured events", FeaturedEvent, FEATURED_EVENTS)
        seed_ordered("Upcoming events", UpcomingEvent, UPCOMING_EVENTS)
        seed_collection("Past events", PastEvent, GALLERY_ITEMS, "title")
        seed_navbar_settings()
        seed_navbar_items()
        seed_footer_settings()
        seed_collection("Footer links", FooterLink, FOOTER_LINKS, "label")
        seed_collection("Footer focus", FooterFocusItem, FOOTER_FOCUS, "title")

        retire_unsplash(HeroBanner, ["image_url"])
        retire_unsplash(HomeProject, ["image_url"])
        retire_unsplash(HomeGalleryItem, ["image_url"])
        retire_unsplash(HomeEvent, ["image_url"])
        retire_unsplash(Testimonial, ["profile_image"])
        retire_unsplash(FeaturedEvent, ["banner_image"])
        retire_unsplash(UpcomingEvent, ["image_url"])
        retire_unsplash(PastEvent, ["image_url"])
        retire_names_not_in(Testimonial, "name", [t["name"] for t in TESTIMONIALS])
        retire_names_not_in(PastEvent, "title", [t["title"] for t in GALLERY_ITEMS])
        retire_names_not_in(UpcomingEvent, "title", [t["title"] for t in UPCOMING_EVENTS])
        retire_names_not_in(HomeProject, "title", [t["title"] for t in HOME_PROJECTS])
        retire_names_not_in(HeroBanner, "title", [t["title"] for t in HERO_BANNERS])

        db.session.commit()
        print("Done. Seeded items are status=published with local AMP images.")


if __name__ == "__main__":
    main()
