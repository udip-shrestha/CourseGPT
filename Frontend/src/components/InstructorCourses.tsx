import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom"; // Added useParams
import { Search, Filter, Plus } from "lucide-react"; // Added Plus
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { CourseCard } from "./CourseCard";
import { CourseRegisterDialog } from "./CourseRegisterDialog"; // Import the new dialog
import { Dialog, DialogTrigger } from "./ui/dialog"; // Import Dialog primitives

// Updated interface to match API response for the list
// Note: Fields like code, studentCount, documentCount, lastUpdated, color are NOT in the API response for this endpoint
export interface CourseSummary {
    id: string; // Course UUID
    instructor_id: string;
    name: string;
    institution: string;
    semester_id: number; // API returns numeric ID
    year: number;
    created_at: string; // ISO date string
}

export function InstructorCourses() {
    const { instructorId } = useParams<{ instructorId: string }>(); // Get instructorId from URL
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState("");
    const [courses, setCourses] = useState<CourseSummary[]>([]); // State for fetched courses
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isRegisterDialogOpen, setIsRegisterDialogOpen] = useState(false); // State for dialog visibility


    // --- Fetch Courses ---
    const fetchCourses = async () => {
        if (!instructorId) return; // Don't fetch if no ID

        setIsLoading(true);
        setError(null);
        // Construct URL with sorting (newest first)
        const url = `http://localhost:8000/instructors/${instructorId}/courses?order_by=created_at&order_dir=desc`;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                // Try parsing error detail
                let errorDetail = `Failed to fetch courses (Status: ${response.status})`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                } catch (_) { /* Ignore if response isn't JSON */ }
                throw new Error(errorDetail);
            }
            const data: CourseSummary[] = await response.json();
            setCourses(data);
        } catch (err: any) {
            console.error("Fetch courses error:", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server.");
            } else {
                setError(err.message || "An error occurred while fetching courses.");
            }
        } finally {
            setIsLoading(false);
        }
    };

    // Fetch courses on initial load or when instructorId changes
    useEffect(() => {
        fetchCourses();
    }, [instructorId]);
    // --- End Fetch Courses ---


    // Navigate to the full course page (we'll implement this later)
    const handleViewCourse = (courseId: string) => {
        // This navigation target might need adjustment based on your full CoursePage component
        navigate(`/courses/${courseId}`); // Assuming a route like this exists
        console.log("Navigate to view course:", courseId); // Placeholder
    };

    // Callback function for when a new course is created by the dialog
    const handleCourseCreated = () => {
        setIsRegisterDialogOpen(false); // Close the dialog
        fetchCourses(); // Re-fetch the course list to show the new one
    };


    // Client-side filtering based on search term
    const filteredCourses = courses.filter((course) =>
        course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.institution.toLowerCase().includes(searchTerm.toLowerCase()) // Filter by institution too?
    );

    // Render loading/error states
    if (isLoading) {
        return <div className="text-center p-10">Loading courses...</div>;
    }

    if (error) {
        return <div className="text-center text-destructive p-10">Error: {error}</div>;
    }

    return (
        // Removed container/mx-auto as layout is handled by App.tsx
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">My Courses</h1>
                {/* --- Register Course Button and Dialog Trigger --- */}
                <Dialog open={isRegisterDialogOpen} onOpenChange={setIsRegisterDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="h-4 w-4 mr-2" />
                            Register New Course
                        </Button>
                    </DialogTrigger>
                    {/* Pass instructorId and callback */}
                    <CourseRegisterDialog
                        instructorId={instructorId!} // Assert non-null as we check above
                        onCourseCreated={handleCourseCreated}
                        onClose={() => setIsRegisterDialogOpen(false)}
                    />
                </Dialog>
                {/* --- End Register Course Button --- */}
            </div>

            {/* Search + Filter */}
            <div className="flex gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search courses by name or institution..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                    />
                </div>
                {/* Keep filter button, functionality TBD */}
                <Button variant="outline">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                </Button>
            </div>

            {/* Course Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map((course) => (
                    <CourseCard
                        key={course.id}
                        course={course} // Pass the course data matching CourseSummary
                        onViewCourse={handleViewCourse}
                    />
                ))}
            </div>

            {/* No Courses Message */}
            {filteredCourses.length === 0 && courses.length > 0 && (
                <p className="text-center text-muted-foreground mt-10">
                    No courses match your search term.
                </p>
            )}
            {courses.length === 0 && (
                <p className="text-center text-muted-foreground mt-10">
                    You haven't registered any courses yet.
                </p>
            )}
        </div>
    );
}

