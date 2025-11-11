import { useState } from "react";
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
// --- 1. IMPORT THE API CLIENT HOOK ---
import { useApiClient } from "../ApiClientContext";

// Define props for the dialog
interface CourseRegisterDialogProps {
    instructorId: string;
    onCourseCreated: () => void; // Callback to refresh course list
    onClose: () => void; // Callback to close dialog from parent state
}


// Based on Swagger, Fall=4, but usually Spring=1, Summer=2, Fall=3. Double-check your DB/backend logic.
const semesterMap: { [key: string]: number } = {
    "Spring": 1, // Placeholder
    "Summer": 2, // Placeholder
    "Fall": 4    // Based on POST /courses
};
const semesterOptions = ["Spring", "Summer", "Fall"]; // Options for the dropdown


export function CourseRegisterDialog({ instructorId, onCourseCreated, onClose }: CourseRegisterDialogProps) {
    // --- 2. INITIALIZE THE API CLIENT ---
    const apiClient = useApiClient();

    const [name, setName] = useState("");
    const [institution, setInstitution] = useState("");
    const [semesterName, setSemesterName] = useState(""); // Store the selected name (e.g., "Fall")
    const [year, setYear] = useState<number | string>("");

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // --- 3. REPLACED 'handleSubmit' TO USE 'apiClient' ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- Validation (remains the same) ---
        if (!name || !institution || !semesterName || !year) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }
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
        const courseData = {
            name: name,
            institution: institution,
            semester_id: semesterId,
            year: numericYear
        };

        console.log("Submitting New Course via ApiClient with data:", courseData);

        // --- API CALL using ApiClient ---
        try {
            // This now calls the 'createCourse' function from ApiClient.ts
            // which handles the query params, auth token, and
            // uses the CORRECT URL: /instructors/{id}/courses
            const { data, errorMessage } = await apiClient.createCourse(instructorId, courseData);

            if (errorMessage) {
                // If the backend sends an error, display it
                throw new Error(errorMessage);
            }

            console.log('Course creation successful:', data);
            onCourseCreated(); // Trigger refresh in parent and close dialog

        } catch (err: any) {
            console.error("Course creation failed:", err);
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
        // The JSX (visuals) remains exactly the same
        <DialogContent className="max-w-lg">
            <DialogHeader>
                <DialogTitle>Register New Course</DialogTitle>
                <DialogDescription>Enter the details for the new course.</DialogDescription>
            </DialogHeader>
            {/* Form layout using grid for alignment */}
            <form onSubmit={handleSubmit} className="grid gap-4 py-4">
                {/* Course Name */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="courseName-dialog" className="text-right">Name</Label>
                    <Input
                        id="courseName-dialog"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="col-span-3"
                        placeholder="e.g., Data Structures"
                        required
                    />
                </div>
                {/* Institution */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="institution-dialog" className="text-right">Institution</Label>
                    <Input
                        id="institution-dialog"
                        value={institution}
                        onChange={(e) => setInstitution(e.target.value)}
                        className="col-span-3"
                        placeholder="e.g., Iowa State University"
                        required
                    />
                </div>
                {/* Semester */}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="semester-dialog" className="text-right">Semester</Label>
                    <Select value={semesterName} onValueChange={setSemesterName} required>
                        <SelectTrigger id="semester-dialog" className="col-span-3">
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
                    <Label htmlFor="year-dialog" className="text-right">Year</Label>
                    <Input
                        id="year-dialog"
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

                {/* Use DialogFooter for buttons */}
                <DialogFooter>
                    <DialogClose asChild>
                        <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>Cancel</Button>
                    </DialogClose>
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? "Registering..." : "Register Course"}
                    </Button>
                </DialogFooter>
            </form>
        </DialogContent>
    );
}