import { useState } from 'react';
import { Calendar, Building, Settings, Trash2, AlertTriangle, Pencil } from 'lucide-react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import type { CourseSummary } from './InstructorCourses';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "./ui/popover";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "./ui/dialog";
// Import the new Update Dialog
import { CourseUpdateDialog } from './CourseUpdateDialog';

// Interface for props using the API data structure
interface CourseCardProps {
    course: CourseSummary;
    onViewCourse: () => void;
    onDelete: () => Promise<void>;
    onCourseUpdated: () => void; // Added onCourseUpdated prop
}

// Helper to convert semester ID to string
function semesterIdToString(id: number): string {
    switch (id) {
        case 1: return "Spring";
        case 2: return "Summer";
        case 3: return "Fall";
        default: return "Unknown";
    }
}

export function CourseCard({ course, onViewCourse, onDelete, onCourseUpdated }: CourseCardProps) {
    const semesterString = semesterIdToString(course.semester_id);

    // State for flows
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isFinalDeleteDialogOpen, setIsFinalDeleteDialogOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState<string | null>(null);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);

    // Delete Handler
    const handleDelete = async () => {
        setIsDeleting(true);
        setDeleteError(null);
        try {
            await onDelete();
            // Close all dialogs on success
            setIsFinalDeleteDialogOpen(false);
            setIsDeleteDialogOpen(false);
            setIsSettingsOpen(false);
        } catch (err: any) {
            console.error("CourseCard delete error:", err);
            setDeleteError(err.message || "An error occurred.");
        } finally {
            setIsDeleting(false);
        }
    };

    // Update Handler
    const handleUpdated = () => {
        setIsUpdateDialogOpen(false); // Close the update dialog
        setIsSettingsOpen(false); // Close the popover
        onCourseUpdated(); // Call the parent's refresh function
    };

    // Click handler for the whole card
    const handleCardClick = () => {
        onViewCourse();
    };

    // Click handler for buttons (stops card click)
    const handleButtonClick = (e: React.MouseEvent) => {
        e.stopPropagation();
    };

    return (
        // Card is now clickable
        <Card
            className="hover:shadow-md transition-shadow relative cursor-pointer"
            onClick={handleCardClick}
        >
            {/* Settings Popover */}
            <div className="absolute top-2 right-2 z-10" onClick={handleButtonClick}>
                <Popover open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                    <PopoverTrigger asChild>
                        <Button variant="ghost" size="icon" aria-label="Course Settings">
                            <Settings className="h-4 w-4" />
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-48 p-2">
                        <div className="grid gap-1">
                            {/* Delete Option (Triggers First Dialog) */}
                            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                                <DialogTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10 text-sm h-8"
                                    >
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        Delete Course
                                    </Button>
                                </DialogTrigger>
                                {/* Delete Dialogs */}
                                <DialogContent>
                                    <DialogHeader>
                                        <DialogTitle>Delete "{course.name}"?</DialogTitle>
                                        <DialogDescription>
                                            Are you sure you want to delete this course? This action cannot be undone.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <DialogFooter className="gap-2 sm:justify-end">
                                        <DialogClose asChild>
                                            <Button variant="outline">Cancel</Button>
                                        </DialogClose>
                                        <Dialog open={isFinalDeleteDialogOpen} onOpenChange={setIsFinalDeleteDialogOpen}>
                                            <DialogTrigger asChild>
                                                <Button variant="destructive">Confirm Delete</Button>
                                            </DialogTrigger>
                                            <DialogContent>
                                                <DialogHeader>
                                                    <DialogTitle className="flex items-center gap-2">
                                                        <AlertTriangle className="text-destructive h-5 w-5" />
                                                        Final Confirmation
                                                    </DialogTitle>
                                                    <DialogDescription>
                                                        This will permanently delete the course and all its documents. This action cannot be recovered.
                                                        {deleteError && <p className="text-sm text-destructive mt-4">Error: {deleteError}</p>}
                                                    </DialogDescription>
                                                </DialogHeader>
                                                <DialogFooter className="gap-2">
                                                    <Button
                                                        variant="outline"
                                                        onClick={() => setIsFinalDeleteDialogOpen(false)}
                                                        disabled={isDeleting}
                                                    >
                                                        Cancel
                                                    </Button>
                                                    <Button
                                                        variant="destructive"
                                                        onClick={handleDelete}
                                                        disabled={isDeleting}
                                                    >
                                                        {isDeleting ? "Deleting..." : "Yes, Delete Permanently"}
                                                    </Button>
                                                </DialogFooter>
                                            </DialogContent>
                                        </Dialog>
                                    </DialogFooter>
                                </DialogContent>
                            </Dialog>
                        </div>
                    </PopoverContent>
                </Popover>
            </div>
            {/* --- END SETTINGS POPOVER --- */}

            <CardHeader className="pb-3 pr-10">
                <div className="space-y-1">
                    <h3 className="font-semibold leading-tight text-lg">{course.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Building className="h-4 w-4" />
                        <span>{course.institution}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>{semesterString} {course.year}</span>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="pt-2">
                <div className="pt-4 mt-4 border-t">
                    {/* "Update Course" button */}
                    <Dialog open={isUpdateDialogOpen} onOpenChange={setIsUpdateDialogOpen}>
                        <DialogTrigger asChild>
                            <Button
                                variant="outline"
                                className="w-full"
                                onClick={handleButtonClick} // Stop propagation
                            >
                                <Pencil className="mr-2 h-4 w-4" />
                                Update Course
                            </Button>
                        </DialogTrigger>
                        {/* This renders the new update form */}
                        <CourseUpdateDialog
                            course={course}
                            onCourseUpdated={handleUpdated}
                            onClose={() => setIsUpdateDialogOpen(false)}
                        />
                    </Dialog>
                </div>
            </CardContent>
        </Card>
    );
}