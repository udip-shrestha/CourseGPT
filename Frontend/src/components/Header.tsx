import { GraduationCap, User, Upload } from 'lucide-react';
import { Button } from './ui/button';

interface HeaderProps {
  activeSection: 'profile' | 'courses';
  onSectionChange: (section: 'profile' | 'courses') => void;
}

export function Header({ activeSection, onSectionChange }: HeaderProps) {
  return (
    <header className="border-b bg-card">
      <div className=" px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold text-primary">CourseGPT</h1>
          </div>

          <nav className="flex items-center gap-4">
            <Button
              variant={activeSection === 'profile' ? 'default' : 'ghost'}
              onClick={() => onSectionChange('profile')}
              className="flex items-center gap-2"
            >
              <User className="h-4 w-4" />
              Profile
            </Button>
            <Button
              variant={activeSection === 'courses' ? 'default' : 'ghost'}
              onClick={() => onSectionChange('courses')}
              className="flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Courses
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
}