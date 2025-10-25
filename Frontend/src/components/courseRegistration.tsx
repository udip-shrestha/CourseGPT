import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea"; // Import Textarea
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"; // Import Select components
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

// Placeholder data - replace with actual API fetch later
const instructors = [
    { id: "1", name: "Dr. Sarah Johnson" },
    { id: "2", name: "Prof. Alex Chen" },
    { id: "3", name: "Dr. Emily Carter" },
];

export function RegisterPage() {
    const navigate = useNavigate(); // Hook for navigation
    const [courseName, setCourseName] = useState("");
    const [semester, setSemester] = useState<"Fall" | "Spring" | "Summer" | "">("");
    const [year, setYear] = useState<number | string>(""); // Use string initially for input
    const [instructorId, setInstructorId] = useState("");
    const [description, setDescription] = useState("");
    const [credits, setCredits] = useState<number | string>(""); // Use string initially for input

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // Basic validation (more robust validation needed in a real app)
        if (!courseName || !semester || !year || !instructorId || !description || !credits) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }

        const courseData = {
            course_name: courseName,
            semester: semester,
            year: Number(year), // Convert year to number
            instructor_id: instructorId, // Assuming ID is string from select
            course_description: description,
            credit_points: Number(credits), // Convert credits to number
        };

        console.log("Submitting Course Registration:", courseData);

        // --- Replace with your actual API call ---
        try {
            // Example:
            // const response = await fetch('/api/courses/register', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify(courseData),
            // });
            // if (!response.ok) {
            //   const errorData = await response.json();
            //   throw new Error(errorData.detail || 'Registration failed');
            // }
            // const result = await response.json();
            // console.log('Registration successful:', result);
            // navigate(`/courses/${result.courseId}`); // Navigate to the new course page

            // Simulate API call for now
            await new Promise(resolve => setTimeout(resolve, 1500));
            console.log("Simulated registration successful");
            navigate(`/instructors/${instructorId}/courses`); // Navigate back to courses list or similar


        } catch (err: any) {
            console.error("Registration failed:", err);
            setError(err.message || "An unexpected error occurred.");
        } finally {
            setIsLoading(false);
        }
        // --- End of API call section ---
    };

    return (
        // Centering container - make sure it works with your App.tsx layout
        <div className="w-full flex items-center justify-center p-4">
            {/* Responsive Card: full width on small screens, max width on larger */}
            <Card className="w-full max-w-lg shadow-md">
                <CardHeader>
                    <CardTitle>Register New Course</CardTitle>
                    <CardDescription>Enter the details for the new course.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        {/* Course Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="courseName">Course Name</Label>
                            <Input
                                id="courseName"
                                type="text"
                                placeholder="e.g., Introduction to AI"
                                value={courseName}
                                onChange={(e) => setCourseName(e.target.value)}
                                required
                            />
                        </div>

                        {/* Semester and Year (side-by-side) */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label htmlFor="semester">Semester</Label>
                                <Select
                                    value={semester}
                                    onValueChange={(value) => setSemester(value as "Fall" | "Spring" | "Summer")} // Type assertion
                                    required
                                >
                                    <SelectTrigger id="semester">
                                        <SelectValue placeholder="Select semester" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Fall">Fall</SelectItem>
                                        <SelectItem value="Spring">Spring</SelectItem>
                                        <SelectItem value="Summer">Summer</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="year">Year</Label>
                                <Input
                                    id="year"
                                    type="number"
                                    placeholder="e.g., 2024"
                                    value={year}
                                    onChange={(e) => setYear(e.target.value)}
                                    required
                                    min="2000" // Example validation
                                />
                            </div>
                        </div>

                        {/* Instructor */}
                        <div className="grid gap-2">
                            <Label htmlFor="instructor">Instructor</Label>
                            <Select value={instructorId} onValueChange={setInstructorId} required>
                                <SelectTrigger id="instructor">
                                    <SelectValue placeholder="Select instructor" />
                                </SelectTrigger>
                                <SelectContent>
                                    {instructors.map((inst) => (
                                        <SelectItem key={inst.id} value={inst.id}>
                                            {inst.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Description */}
                        <div className="grid gap-2">
                            <Label htmlFor="description">Course Description</Label>
                            <Textarea
                                id="description"
                                placeholder="Enter a brief description of the course..."
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                required
                                rows={4} // Adjust height as needed
                            />
                        </div>

                        {/* Credits */}
                        <div className="grid gap-2">
                            <Label htmlFor="credits">Credit Points</Label>
                            <Input
                                id="credits"
                                type="number"
                                placeholder="e.g., 3"
                                value={credits}
                                onChange={(e) => setCredits(e.target.value)}
                                required
                                min="0" // Example validation
                            />
                        </div>

                        {/* Error Message */}
                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {/* Submit Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Registering..." : "Register Course"}
                        </Button>
                        {/* Link back to Login (Optional) */}
                        <Button
                            type="button"
                            variant="link"
                            className="w-full"
                            onClick={() => navigate('/login')} // Navigate back to login
                        >
                            Back to Login
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}