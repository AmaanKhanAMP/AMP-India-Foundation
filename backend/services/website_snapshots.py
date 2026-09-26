"""Approved public-website copy for chatbot indexing.

These pages are not CMS-managed (About, Projects, Support). Keep this text
aligned with the live frontend. CMS-managed events/contact/home still come
from MySQL via chatbot_sync._export_cms_sources.
"""

from __future__ import annotations

from typing import Dict


def website_about() -> str:
    return """# AMP India Foundation — About (approved website)

AMP India Foundation (AIF) is a registered non-profit organization committed to empowering underprivileged individuals and communities through sustainable development initiatives.

Hero: Empowering Lives. Transforming Communities.
At AMP India Foundation, we believe that every individual deserves an opportunity to learn, earn and live with dignity. Through education, employment, healthcare, skill development and community empowerment, we work to create lasting change for underprivileged communities across India.

## Focus areas
Education: Supporting deserving students through scholarships, career guidance, mentoring, digital learning and skill development.
Employment: Preparing youth for successful careers through employability training, job fairs, placement support and industry partnerships.
Skill Development: Providing vocational and technical training that improves employability and creates opportunities for self-employment.
Healthcare: Extending medical assistance, health awareness programmes, medical camps and emergency support to individuals and families in need.
Empowerment: Promoting sustainable livelihoods, financial inclusion, entrepreneurship and social development initiatives that strengthen communities.

## Core values
Compassion: We serve with empathy and respect, placing the dignity of every individual at the centre of our work.
Integrity: We maintain the highest standards of honesty, transparency and accountability in everything we do.
Excellence: We continuously strive to deliver impactful programmes with professionalism and quality.

## What we do
01 Education & Scholarships — Helping deserving students continue their education through scholarships, educational support, mentoring and career guidance.
02 Employability & Career Development — Organising employability training programmes, career counselling sessions, job drives and Mega Job Fairs to connect youth with employment opportunities.
03 Skill Development — Providing vocational and technical training that prepares individuals for today's job market and encourages entrepreneurship.
04 Healthcare Support — Extending medical assistance, health awareness programmes and emergency support to those in need.
05 Community Empowerment — Promoting sustainable livelihoods, financial inclusion and social development initiatives.

## FAQs
What does AMP India Foundation do? AMP India Foundation works in the areas of education, employment, skill development, healthcare and community empowerment to improve the lives of underprivileged individuals across India.
Who can benefit from your programmes? Students, job seekers, women, youth, families and disadvantaged communities from across India can benefit from our various initiatives, subject to the eligibility criteria of each programme.
How can I support the Foundation? You can support our mission by making a donation, volunteering your time and skills, mentoring students, partnering with us, or helping spread awareness about our work.
Can I volunteer with AMP India Foundation? Yes. We welcome students, professionals, entrepreneurs and retirees who wish to contribute their time, expertise and experience towards social development.
Are your programmes open to everyone? Yes. Our initiatives are implemented without discrimination based on caste, community, creed, gender or religion.

Website: /about
"""


def website_projects() -> str:
    return """# AMP India Foundation — Projects (approved website)

Every project at AMP India Foundation is designed to empower individuals and strengthen communities. From education and employment to healthcare and livelihood support, our initiatives help people build brighter, more self-reliant futures.

## Education — Building Brighter Futures
Path: /projects/education
Heading: EDUCATION — SKILL DEVELOPMENT & LIVELIHOOD LIFTS
Quote: Empowering BPL youth through localized technical skill frameworks.
Key initiatives: Scholarships for deserving students; Career Guidance Programmes; Student Mentorship; Educational Support; Centres of Excellence.
Indian youth from BPL families are often unable to continue education after the primary section and must support their families. AIF conducts targeted vocational training for school dropouts in market-driven skills such as mobile repairing, air-conditioning and refrigerator maintenance, water filter repairing, and motor vehicle servicing. Through NSDC-sponsored CSR programmes, AIF delivers free short-term vocational skills training nationwide.

## Employment Assistance — Connecting Talent with Opportunity
Path: /projects/employment
Heading: SUPPORT — CAREER PLACEMENT INFRASTRUCTURE
Quote: Bridging the transition from student networks to corporate ecosystems.
Key initiatives: Employability Training Programmes (ETP); Career Counselling; Mega Job Fairs; Placement Support; Campus Recruitment Drives.
Securing meaningful jobs is a struggle for much of the Indian working class. AIF hosts soft-skills workshops, employability seminars, and large-scale job drives and fairs to connect youth with corporate career avenues.

## Skill Development / Employment Training
Path: /projects/training
Heading: TRAINING — CORPORATE GROOMING & PREPARATION
Quote: Polishing core foundational skills to ensure immediate employment fit.
Key initiatives: Vocational Training; Technical Skills Development; Entrepreneurship Training; Digital Skills; Livelihood Programmes.
AIF conducts the Employability Training Program (ETP) to train youngsters in pre-employment preparation. ETP covers job hunting, resume structuring, interview performance, professional grooming, and communications.

## Medical Relief
Path: /projects/medical and /projects/healthcare
Heading: MEDICAL AID — HEALTHCARE INTERVENTION & OUTREACH
Quote: Breaking barriers to provide essential diagnostic and clinical relief.
Key initiatives: Free Medical Camps; Health Awareness Programmes; Emergency Medical Assistance; Medical Aid for Needy Patients.
AIF coordinates healthcare networks, diagnostic camps, free essential medicine clinics, and emergency financial support for critical tertiary care, without bias of caste, community, creed, or religion.

## Economic Empowerment
Path: /projects/empowerment
Heading: EMPOWERMENT — FINANCIAL INDEPENDENCE SYSTEM
Quote: Cultivating entrepreneurial self-reliance across urban and rural chapters.
Key initiatives: Livelihood Support; Entrepreneurship Promotion; Financial Awareness; Community Development Programmes; Women & Youth Empowerment.
AIF builds voluntary social platforms for long-term self-sufficiency through livelihood assistance, early capital guidance, small enterprise tools, and marketplace connections.

## Mentorship
Path: /projects/mentorship
Heading: MENTORSHIP — INTELLECTUAL GUIDANCE FRAMEWORK
Quote: Connecting industry experience with first-generation student networks.
Key initiatives: One-to-One Mentoring; Career Guidance; Leadership Development; Professional Networking; Soft Skills Training.
AMP connects established professionals with students to share knowledge, experience, and career guidance, especially for first-generation learners.

## Career Guidance
Career Guidance is part of AMP India Foundation education and mentorship work. Students receive counselling on courses, careers, employability, and next steps through seminars, mentoring, and education-support programmes. Website: /projects/education and /projects/mentorship.

Website: /projects
"""


def website_support() -> str:
    return """# AMP India Foundation — Support Us (approved website)

You can support AMP India Foundation through a direct bank transfer, UPI, or cheque/DD.

Bank Name: Kotak Mahindra Bank
Account Name: AMP India Foundation
Account Number: 3114476665
Account Type: Savings Account
IFSC: KKBK0001348
Donations can be made through NEFT, RTGS, IMPS or other online banking channels.

UPI Donation: AMP UPI ID AMPINDIA@KOTAK

Cheque / DD: Yes, cheque and demand draft are accepted.
Cheque/DD in favour of: Association of Muslim Professionals
Mail to: Association of Muslim Professionals, Room 8, 1st Floor, Halima Manzil, Mirza Ghalib Marg, Clare Road, Nagpada, Mumbai – 400008.
Offline donation by cheque is available on the Support Us page.

After your donation, please send a confirmation email to info@ampindia.org with your transfer reference so a donation receipt can be issued.

AMP India Foundation is a Section 8 Company (Non-Profit) registered under the Companies Act, 2013 with the Ministry of Corporate Affairs (MCA). For current 80G / tax-exemption documentation, email info@ampindia.org.

Together for change: Behind every scholarship is a student's dream. Behind every job is a family's hope. Behind every volunteer is a community made stronger.

Website: /support-us
"""


def website_volunteer() -> str:
    return """# AMP India Foundation — Volunteer (approved website)

AMP India Foundation welcomes students, professionals, entrepreneurs and retirees who wish to contribute time, expertise and experience towards social development.

Volunteer registration: https://tinyurl.com/AIFVolunteerRegn
Website: /volunteer
"""


def website_home() -> str:
    return """# AMP India Foundation — Home (approved website)

Hero: Empowering Lives. Transforming Communities.
AMP India Foundation works through education, employment, healthcare, skill development and community empowerment.

## Welcome
WELCOME TO AMP INDIA FOUNDATION
Together, We Create Lasting Change
AMP India Foundation (AIF) is a registered non-profit organization working to improve the lives of underprivileged communities across India. Through education, employment, skill development, healthcare and community empowerment, we help people build better futures with dignity and confidence.
Supported by a nationwide network of professionals, volunteers, donors and partner organizations, we strive to create opportunities that bring lasting social impact.

Home cards:
Education Support — Building Brighter Futures. We help deserving students continue their education through scholarships, mentoring, career guidance and skill development.
Employment Support — Creating Better Career Opportunities. We prepare young people for successful careers through employability training, career counselling, job fairs and placement support.
Mentorship & Guidance — Inspiring the Next Generation. Experienced professionals mentor students and young graduates with knowledge, career advice and life skills.

## Impact statistics (home)
100000+ candidates placed
625+ job drives organised
350+ employability training programmes
110+ mega job fairs conducted

Website: /
"""


def export_website_sources() -> Dict[str, str]:
    return {
        "website_about": website_about(),
        "website_projects": website_projects(),
        "website_support": website_support(),
        "website_volunteer": website_volunteer(),
        "website_home": website_home(),
    }
