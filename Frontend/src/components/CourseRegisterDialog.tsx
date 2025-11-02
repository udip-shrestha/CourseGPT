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
    DialogClose // Import DialogClose
} from "./ui/dialog";

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
    "Fall": 3    // Based on POST /courses
};
const semesterOptions = ["Spring", "Summer", "Fall"]; // Options for the dropdown


export function CourseRegisterDialog({ instructorId, onCourseCreated, onClose }: CourseRegisterDialogProps) {
    const [name, setName] = useState("");
    const [institution, setInstitution] = useState("");
    const [semesterName, setSemesterName] = useState(""); // Store the selected name (e.g., "Fall")
    const [year, setYear] = useState<number | string>("");

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- Validation ---
        if (!name || !institution || !semesterName || !year) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }
        const semesterId = semesterMap[semesterName]; // Get the numeric ID from the selected name
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


        // --- CONSTRUCT URL WITH QUERY PARAMETERS ---
        const params = new URLSearchParams();
        params.append('name', name);
        params.append('institution', institution);
        params.append('semester_id', semesterId.toString()); // Convert ID to string for URL
        params.append('year', numericYear.toString()); // Convert year to string for URL

        // URL includes instructorId in the path
        const url = `http://localhost:8000/courses/${instructorId}?${params.toString()}`;
        console.log("Submitting New Course via URL:", url);
        // --- END URL CONSTRUCTION ---

        // --- API CALL ---
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'accept': 'application/json' },
                // No body needed as data is in query parameters
            });

            if (!response.ok) { // Check if response status is 2xx
                let errorDetail = `Course creation failed (Status: ${response.status})`;
                try {
                    // Try to parse more specific error from backend JSON response
                    const errorData = await response.json();
                    if (Array.isArray(errorData.detail)) { // Handle FastAPI validation errors (list of objects)
                        errorDetail = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join(', ');
                    } else if (errorData.detail) { // Handle single string detail errors
                        errorDetail = errorData.detail;
                    }
                } catch (_) {
                    // If response isn't JSON, try getting plain text
                    errorDetail = await response.text() || errorDetail;
                }
                throw new Error(errorDetail);
            }

            // Assuming 200 OK or 201 Created signifies success based on Swagger
            const result = await response.json();
            console.log('Course creation successful:', result);
            onCourseCreated(); // Trigger refresh in parent component and close dialog

        } catch (err: any) {
            console.error("Course creation failed:", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server. Please ensure it's running and check CORS settings.");
            } else {
                // Display the error message from the backend or the fetch error
                setError(err.message || "An unexpected error occurred.");
            }
        } finally {
            setIsLoading(false);
        }
        // --- End API Call ---
    };


    return (
        // Use DialogContent component provided by ui/dialog
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
                    {/* Use Select component for dropdown */}
                    <Select value={semesterName} onValueChange={setSemesterName} required>
                        <SelectTrigger id="semester-dialog" className="col-span-3">
                            <SelectValue placeholder="Select semester" />
                        </SelectTrigger>
                        <SelectContent>
                            {/* Map over semester names for options */}
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
                        type="number" // Use number input type
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        className="col-span-3"
                        placeholder="e.g., 2025"
                        min="2000" // Example validation
                        required
                    />
                </div>

                {/* Display Error Message */}
                {error && <p className="col-span-4 text-sm text-destructive text-center">{error}</p>}

                {/* Use DialogFooter for buttons */}
                <DialogFooter>
                    {/* DialogClose wraps the Cancel button */}
                    <DialogClose asChild>
                        <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>Cancel</Button>
                    </DialogClose>
                    {/* Submit button */}
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? "Registering..." : "Register Course"}
                    </Button>
                </DialogFooter>
            </form>
        </DialogContent>
    );
}

