/**
 * Local assets and content for the main Projects landing page only.
 * Featured Initiatives remains unchanged in its own component.
 */

import ampAhmedabadWorkshop from '@/src/assets/gallery/amp-ahmedabad-chapter-workshop.png';
import employmentSupportImage from '@/src/assets/employment-support-job-fair.jpg';
import jobFairPic3 from '@/src/assets/job-fair-pic-3.png';
import medicalReliefCamp from '@/src/assets/medical-relief-camp.png';
import economicEmpowermentTailoring from '@/src/assets/economic-empowerment-tailoring.png';
import mentorshipAgraChapter from '@/src/assets/mentorship-agra-chapter.png';
import employmentTrainingWorkshop from '@/src/assets/employment-training-workshop.png';

function assetSrc(image) {
  return typeof image === 'string' ? image : image?.src;
}

export const PROJECT_HERO_BG = assetSrc(employmentSupportImage);
export const MEDICAL_RELIEF_IMAGE = assetSrc(medicalReliefCamp);
export const ECONOMIC_EMPOWERMENT_IMAGE = assetSrc(economicEmpowermentTailoring);
export const MENTORSHIP_IMAGE = assetSrc(mentorshipAgraChapter);
export const EMPLOYMENT_TRAINING_IMAGE = assetSrc(employmentTrainingWorkshop);

/** Overview cards on /projects — each links to an existing individual project route. */
export const PROJECT_CATEGORIES = [
  {
    id: 'education',
    title: 'Education',
    subtitle: 'Building Brighter Futures',
    href: '/projects/education',
    image: assetSrc(ampAhmedabadWorkshop),
    initiatives: [
      'Scholarships for deserving students',
      'Career Guidance Programmes',
      'Student Mentorship',
      'Educational Support',
      'Centres of Excellence',
    ],
  },
  {
    id: 'employment',
    title: 'Employment Assistance',
    subtitle: 'Connecting Talent with Opportunity',
    href: '/projects/employment',
    image: assetSrc(jobFairPic3),
    initiatives: [
      'Employability Training Programmes (ETP)',
      'Career Counselling',
      'Mega Job Fairs',
      'Placement Support',
      'Campus Recruitment Drives',
    ],
  },
  {
    id: 'skill-development',
    title: 'Skill Development',
    subtitle: 'Learning Skills for a Better Tomorrow',
    href: '/projects/training',
    image: EMPLOYMENT_TRAINING_IMAGE,
    initiatives: [
      'Vocational Training',
      'Technical Skills Development',
      'Entrepreneurship Training',
      'Digital Skills',
      'Livelihood Programmes',
    ],
  },
  {
    id: 'medical',
    title: 'Medical Relief',
    subtitle: 'Caring for Health. Supporting Lives.',
    href: '/projects/medical',
    image: MEDICAL_RELIEF_IMAGE,
    initiatives: [
      'Free Medical Camps',
      'Health Awareness Programmes',
      'Emergency Medical Assistance',
      'Medical Aid for Needy Patients',
    ],
  },
  {
    id: 'empowerment',
    title: 'Economic Empowerment',
    subtitle: 'Strengthening Families and Communities',
    href: '/projects/empowerment',
    image: ECONOMIC_EMPOWERMENT_IMAGE,
    initiatives: [
      'Livelihood Support',
      'Entrepreneurship Promotion',
      'Financial Awareness',
      'Community Development Programmes',
      'Women & Youth Empowerment',
    ],
  },
  {
    id: 'mentorship',
    title: 'Mentorship',
    subtitle: 'Guiding the Leaders of Tomorrow',
    href: '/projects/mentorship',
    image: MENTORSHIP_IMAGE,
    initiatives: [
      'One-to-One Mentoring',
      'Career Guidance',
      'Leadership Development',
      'Professional Networking',
      'Soft Skills Training',
    ],
  },
];
