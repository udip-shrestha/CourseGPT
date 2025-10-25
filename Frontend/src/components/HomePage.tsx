import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
// Removed LogIn, kept Info, X
import { Info, X } from 'lucide-react';

export function HomePage() {
    const navigate = useNavigate();
    const [showInstructions, setShowInstructions] = useState(true);

    // Example user data - replace with actual auth context later
    const user = { name: "Instructor" }; // Placeholder

    return (
        // Make the main container relative to position elements inside it
        <div className="relative min-h-[calc(100vh-theme(spacing.40))] w-full"> {/* Adjust min-height based on header/footer */}

            {/* Login Button (Top Right) - REMOVED */}
            {/*
      <div className="absolute top-0 right-0 p-4">
        <Button
          variant="ghost" // Or "outline"
          size="icon"
          onClick={() => navigate('/login')}
          aria-label="Login"
        >
          <LogIn className="h-5 w-5" />
        </Button>
      </div>
      */}

            {/* Main Content (Centered) */}
            <div className="flex flex-col items-center justify-center pt-16 sm:pt-24 space-y-4 text-center">
                {/* Welcome Message (Top Middle) */}
                <h2 className="text-3xl font-semibold tracking-tight">
                    Welcome Back{user ? `, ${user.name}` : ''}!
                </h2>

                <h1 className="text-4xl font-bold md:text-5xl lg:text-6xl text-primary">
                    CourseGPT
                </h1>
                <p className="max-w-xl text-lg text-muted-foreground">
                    Your AI assistant for managing course materials and generating insights.
                </p>

                {/* --- Test Buttons --- */}
                <div className="flex gap-4 pt-4">
                    <Button
                        variant="secondary" // Use a secondary style
                        onClick={() => navigate('/instructors/1/profile')} // Use a specific ID or placeholder
                    >
                        Go to Test Instructor Profile
                    </Button>
                    <Button
                        variant="outline" // Example for courses
                        onClick={() => navigate('/instructors/1/courses')} // Use a specific ID or placeholder
                    >
                        Go to Test Instructor Courses
                    </Button>
                </div>
                {/* --- END --- */}

            </div>

            {/* Instruction Pop-up (Bottom Left) */}
            {showInstructions && (
                <div className="absolute bottom-4 left-4 w-full max-w-sm">
                    <Card className="bg-card text-card-foreground border shadow-lg">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium flex items-center gap-2">
                                <Info className="h-4 w-4 text-primary" />
                                Quick Guide
                            </CardTitle>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => setShowInstructions(false)}
                                aria-label="Close instructions"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </CardHeader>
                        <CardContent>
                            <p className="text-xs text-muted-foreground">
                                Here's some default information on how to integrate content.
                                Use the header links to navigate between your profile and courses.
                                Click the login icon to sign in.
                                questions? (yes) (no)
                            </p>
                            {/* Add more specific instructions later */}
                        </CardContent>
                    </Card>
                </div>
            )}

        </div>
    );
}

