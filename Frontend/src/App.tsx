import { useState } from 'react';
import { Header } from './components/Header';
import { InstructorProfile } from './components/InstructorProfile';
import { CourseManager } from './components/CourseManager';

export default function App() {
  const [activeSection, setActiveSection] = useState<'profile' | 'courses'>('profile');

  return (
    <div className="min-h-screen bg-background">
      <Header activeSection={activeSection} onSectionChange={setActiveSection} />
      
      <main>
        {activeSection === 'profile' && <InstructorProfile />}
        {activeSection === 'courses' && <CourseManager />}
      </main>
    </div>
  );
}
