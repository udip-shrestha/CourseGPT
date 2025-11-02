import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
// Import Dialog components
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogClose // Added DialogClose for convenience
} from './ui/dialog';
import { Info, X } from 'lucide-react'; // Kept Info, X

export function HomePage() {
    const navigate = useNavigate();
    const [showInstructions, setShowInstructions] = useState(true);
    // State for the second help dialog
    const [isHelpDialogOpen, setIsHelpDialogOpen] = useState(false);

    // Example user data - replace with actual auth context later
    const user = { name: "Instructor" }; // Placeholder

    const handleYesClick = () => {
        setShowInstructions(false); // Close the first pop-up
        setIsHelpDialogOpen(true); // Open the dialog
    };

    const handleNoClick = () => {
        setShowInstructions(false); // Close the first pop-up
    };


    return (
        // Make the main container relative to position elements inside it
        <div className="relative w-full flex flex-col items-center justify-center py-16 sm:py-24 space-y-4 text-center">

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
                            {/* Use the "No" click handler for the X button as well */}
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={handleNoClick}
                                aria-label="Close instructions"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </CardHeader>
                        <CardContent>
                            <p className="text-xs text-muted-foreground mb-3"> {/* Added margin-bottom */}
                                Here's some default information on how to integrate content.
                                Use the header links to navigate between your profile and courses.
                                Need more specific instructions?
                            </p>
                            {/* Yes/No Buttons */}
                            <div className="flex justify-end gap-2">
                                <Button variant="outline" size="sm" onClick={handleNoClick}>
                                    No
                                </Button>
                                <Button variant="default" size="sm" onClick={handleYesClick}>
                                    Yes
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* --- Help Dialog --- */}
            <Dialog open={isHelpDialogOpen} onOpenChange={setIsHelpDialogOpen}>
                <DialogContent className="max-w-md"> {/* Adjust width as needed */}
                    <DialogHeader>
                        <DialogTitle>Detailed Instructions</DialogTitle>
                        <DialogDescription>
                            Here are some common tasks:
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-3 py-4 max-h-[60vh] overflow-y-auto"> {/* Added scroll */}
                        {/* Instruction Items */}
                        <div className="border rounded-md p-3 text-sm">
                            <h4 className="font-medium mb-1">How to use ChatBot in Discord</h4>
                            <p className="text-muted-foreground text-xs">
                                Detailed steps on integrating and using the CourseGPT bot within Discord channels...
                            </p>
                        </div>
                        <div className="border rounded-md p-3 text-sm">
                            <h4 className="font-medium mb-1">How students register for Discord</h4>
                            <p className="text-muted-foreground text-xs">
                                Instructions for students on joining the Discord server and verifying their accounts...
                            </p>
                        </div>
                        <div className="border rounded-md p-3 text-sm">
                            <h4 className="font-medium mb-1">Uploading Course Materials</h4>
                            <p className="text-muted-foreground text-xs">
                                Go to the 'Courses' section, select your course, and use the 'Add Document' button...
                            </p>
                        </div>
                        {/* for more instruction boxes here later */}

                    </div>
                    {/* Add a close button to the dialog footer */}
                    <div className="flex justify-end">
                        <DialogClose asChild>
                            <Button variant="outline">Close</Button>
                        </DialogClose>
                    </div>
                </DialogContent>
            </Dialog>
            {/* --- Help Dialog --- */}

        </div>
    );
}

