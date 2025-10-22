import { useState } from 'react';
import { Header } from './components/Header';
import { InstructorProfile } from './components/InstructorProfile';
import { CourseManager } from './components/CourseManager';
import {ThemeCustomizer} from "./components/ThemeCustomizer"; // Correct import
// (Optional) import SizeDebugger if you want to test layout scaling
// import { SizeDebugger } from './components/SizeDebugger';

export default function App() {
    const [activeSection, setActiveSection] = useState<'profile' | 'courses'>('profile');

    return (
        // The main div uses the --custom-foreground variable if set
        <div className="min-h-screen bg-background text-[color:var(--custom-foreground,var(--foreground))] transition-all duration-300">
            {/* Header */}
            <Header activeSection={activeSection} onSectionChange={setActiveSection} />

            {/* Main content area */}
            <main className=" px-6 sm:px-8 py-10">
                {activeSection === 'profile' && <InstructorProfile />}
                {activeSection === 'courses' && <CourseManager />}
            </main>

            {/* (Optional) Live screen width debugger for testing responsiveness */}
            {/* <SizeDebugger /> */}

            {/* --- ADD THIS SECTION --- */}
            <footer className="px-6 sm:px-8 py-10 flex justify-center">
                <ThemeCustomizer />
            </footer>
            {/* --- END OF ADDED SECTION --- */}
        </div>
    );
}

