import { Routes, Route } from 'react-router-dom';
import Navbar from '../src/components/layout/Navbar.jsx';
import Footer from '../src/components/layout/Footer.jsx';
import '../src/App.css';
import Home from '../src/pages/Home.jsx';
import About from '../src/pages/About.jsx';
import Events from '../src/pages/Events.jsx';
import Support from '../src/pages/Support.jsx';
import Contact from '../src/pages/Contact.jsx';
import Education from '../src/pages/projects/Education.jsx';
import Medical from '../src/pages/projects/Medical.jsx';
import FeaturedInitiatives from '../src/components/layout/FeaturedInitiative.jsx';
import Employment from '../src/pages/projects/Employment.jsx';
import Empowerment from '../src/pages/projects/Empowerment.jsx';
import Mentorship from '../src/pages/projects/Mentorship.jsx';
import Training from '../src/pages/projects/Training.jsx';
import Volunteer from '../src/pages/Volunteer.jsx';

// Archived React Router app shell — kept for reference during Next.js migration.
// Note: many src/* files now re-export from the Next.js @/components tree.
function App() {
  return (
    <>
      <Navbar />
      <main style={{ minHeight: '80vh' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/events" element={<Events />} />
          <Route path="/volunteer" element={<Volunteer />} />
          <Route path="/support" element={<Support />} />
          <Route path="/support-us" element={<Support />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/what-we-do" element={<About />} />
          <Route path="/projects" element={<FeaturedInitiatives />} />
          <Route path="/projects/education" element={<Education />} />
          <Route path="/projects/featured" element={<FeaturedInitiatives />} />
          <Route path="/projects/medical" element={<Medical />} />
          <Route path="/projects/employment" element={<Employment />} />
          <Route path="/projects/empowerment" element={<Empowerment />} />
          <Route path="/projects/mentorship" element={<Mentorship />} />
          <Route path="/projects/training" element={<Training />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <Footer />
    </>
  );
}

export default App;
