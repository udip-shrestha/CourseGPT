import { useState } from 'react';
import { Header } from './components/Header';
import { InstructorProfile } from './components/InstructorProfile';
import { CourseManager } from './components/CourseManager';
// (Optional) import SizeDebugger if you want to test layout scaling
// import { SizeDebugger } from './components/SizeDebugger';

export default function App() {
    const [activeSection, setActiveSection] = useState<'profile' | 'courses'>('profile');

    return (
        <div className="min-h-screen bg-background text-foreground transition-all duration-300">
            {/* Header */}
            <Header activeSection={activeSection} onSectionChange={setActiveSection} />

            {/* Main content area */}
            <main className="container-wide mx-auto px-6 sm:px-8 py-10">
                {activeSection === 'profile' && <InstructorProfile />}
                {activeSection === 'courses' && <CourseManager />}
            </main>

            {/* (Optional) Live screen width debugger for testing responsiveness */}
            {/* <SizeDebugger /> */}
        </div>
    );
}
