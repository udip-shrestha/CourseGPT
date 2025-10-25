import {useState} from 'react';
import {Header} from './components/Header';

export function Login() {
    const [activeSection, setActiveSection] = useState<'profile' | 'courses'>('profile');

    const handleSectionChange = (section: 'profile' | 'courses') => {
        setActiveSection(section);
    };


    return (
        <div className="min-h-screen bg-background">
            <Header
                activeSection={activeSection}
                onSectionChange={handleSectionChange}
            />

            <main className="container mx-auto px-4 py-8">
                {activeSection === 'profile' && (
                    <div className="space-y-6">
                        <h2 className="text-3xl font-bold">Profile</h2>
                        <p className="text-muted-foreground">
                            Manage your profile information and settings.
                        </p>
                        {/* Add your profile content here */}
                    </div>
                )}

                {activeSection === 'courses' && (
                    <div className="space-y-6">
                        <h2 className="text-3xl font-bold">Courses</h2>
                        <p className="text-muted-foreground">
                            Upload and manage your course materials.
                        </p>
                        {/* Add your courses content here */}
                    </div>
                )}
            </main>
        </div>
    );
}