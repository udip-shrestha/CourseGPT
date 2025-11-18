import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import {
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogClose
} from "./ui/dialog";
import { useApiClient } from "../ApiClientContext";
import type { CourseSummary } from "./InstructorCourses"; // Import the type

// Define props for the dialog
interface CourseUpdateDialogProps {
    course: CourseSummary; // Pass in the course data to pre-fill
    onCourseUpdated: () => void; // Callback to refresh course list
    onClose: () => void; // Callback to close dialog
}

// --- Semester Mapping (Matches CourseRegisterDialog) ---
const semesterMap: { [key: string]: number } = {
    "Spring": 1,
    "Summer": 2,
    "Fall": 3,
};
const semesterOptions = ["Spring", "Summer", "Fall"];

// Helper to find semester name from ID
function semesterIdToName(id: number): string {
    return Object.keys(semesterMap).find(key => semesterMap[key] === id) || "Fall";
}
// --- End Helpers ---


export function CourseUpdateDialog({ course, onCourseUpdated, onClose }: CourseUpdateDialogProps) {
    const apiClient = useApiClient();

    // --- State is pre-filled from the 'course' prop ---
    const [name, setName] = useState(course.name);
    const [institution, setInstitution] = useState(course.institution);
    const [semesterName, setSemesterName] = useState(semesterIdToName(course.semester_id));
    const [year, setYear] = useState<number | string>(course.year);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Update state if the course prop changes (e.g., opening dialog for a different course)
    useEffect(() => {
        setName(course.name);
        setInstitution(course.institution);
        setSemesterName(semesterIdToName(course.semester_id));
        setYear(course.year);
    }, [course]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- Validation ---
        const semesterId = semesterMap[semesterName];
        if (semesterId === undefined) {
            setError("Invalid semester selected.");
            setIsLoading(false);
            return;
        }
        const numericYear = Number(year);
        if (isNaN(numericYear) || numericYear < 2000) {
            setError("Please enter a valid year (e.g., 2024 or later).");
            setIsLoading(false);
            return;
        }
        // --- End Validation ---

        // Data object to pass to the API client
        // Only include fields that are part of the PUT endpoint
        const courseData = {
            name: name,
            institution: institution,
            semester_id: semesterId,
            year: numericYear
        };

        console.log(`Updating Course ${course.id} via ApiClient with data:`, courseData);

        // --- API CALL using ApiClient ---
        try {
            const { data, errorMessage } = await apiClient.updateCourse(course.id, courseData);

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            console.log('Course update successful:', data);
            onCourseUpdated(); // Trigger refresh in parent and close dialog

        } catch (err: any) {
            console.error("Course update failed:", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server. Please ensure it's running and check CORS settings.");
            } else {
                setError(err.message || "An unexpected error occurred.");
            }
        } finally {
            setIsLoading(false);
        }
        // --- End API Call ---
    };


    return (
        <DialogContent className="max-w-lg">
            <DialogHeader>
                <DialogTitle>Update Course</DialogTitle>
                <DialogDescription>
                    Make changes to "{course.name}". Only provided fields will be updated.
                </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="grid gap-4 py-4">
                {/* Course Name */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="courseName-update" className="text-right">Name</Label>
                    <Input
                        id="courseName-update"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="col-span-3"
                        required
                    />
                </div>
                {/* Institution */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="institution-update" className="text-right">Institution</Label>
                    <Input
                        id="institution-update"
                        value={institution}
                        onChange={(e) => setInstitution(e.target.value)}
                        className="col-span-3"
                        required
                    />
                </div>
                {/* Semester */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="semester-update" className="text-right">Semester</Label>
                    <Select value={semesterName} onValueChange={setSemesterName} required>
                        <SelectTrigger id="semester-update" className="col-span-3">
                            <SelectValue placeholder="Select semester" />
                        </SelectTrigger>
                        <SelectContent>
                            {semesterOptions.map((sem) => (
                                <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
                {/* Year */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="year-update" className="text-right">Year</Label>
                    <Input
                        id="year-update"
                        type="number"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        className="col-span-3"
                        placeholder="e.g., 2025"
                        min="2000"
                        required
                    />
                </div>

                {/* Display Error Message */}
                {error && <p className="col-span-4 text-sm text-destructive text-center">{error}</p>}

                <DialogFooter>
                    <DialogClose asChild>
                        <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>Cancel</Button>
                    </DialogClose>
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? "Saving Changes..." : "Save Changes"}
                    </Button>
                </DialogFooter>
            </form>
        </DialogContent>
    );
}