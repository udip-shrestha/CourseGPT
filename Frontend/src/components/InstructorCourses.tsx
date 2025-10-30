import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Search, Filter, Plus } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { CourseCard } from "./CourseCard";
import { CourseRegisterDialog } from "./CourseRegisterDialog";
import { Dialog, DialogTrigger } from "./ui/dialog";

export interface CourseSummary {
    id: string;
    instructor_id: string;
    name: string;
    institution: string;
    semester_id: number;
    year: number;
    created_at: string;
}

export function InstructorCourses() {
    // --- Get instructorId from URL ---
    const { instructorId } = useParams<{ instructorId: string }>();
    // --- ADDED LOG: Log ID on initial render ---
    console.log("--- InstructorCourses Component Render ---");
    console.log("instructorId from useParams:", instructorId);
    // ------------------------------------------

    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState("");
    const [courses, setCourses] = useState<CourseSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true); // Default to true
    const [error, setError] = useState<string | null>(null);
    const [isRegisterDialogOpen, setIsRegisterDialogOpen] = useState(false);

    // --- Fetch Courses Effect ---
    useEffect(() => {
        console.log("--- useEffect Running ---");
        console.log("instructorId inside useEffect:", instructorId);

        // --- Robust Guard ---
        if (!instructorId || instructorId === "undefined") {
            console.error("GUARD: Instructor ID is missing or invalid, stopping fetch.", instructorId);
            // Don't set loading to false here immediately if it might become valid later
            // setError("Instructor ID is missing or invalid in URL.");
            // setIsLoading(false); // Let's remove this for now
            return; // Stop the effect
        }
        // --- End Guard ---

        // If we pass the guard, proceed with fetch
        console.log("GUARD PASSED: Proceeding with fetch for instructorId:", instructorId);
        setIsLoading(true); // Ensure loading is true before fetch starts
        setError(null); // Clear previous errors

        const fetchCourses = async () => {
            const url = `http://localhost:8000/instructors/${instructorId}/courses?order_by=created_at&order_dir=desc`;
            console.log("Fetching courses from:", url);

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    let errorDetail = `Failed to fetch courses (Status: ${response.status})`;
                    // ... (rest of error parsing remains the same) ...
                    try {
                        const errorData = await response.json();
                        if (Array.isArray(errorData.detail)) {
                            errorDetail = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join(', ');
                        } else if (errorData.detail) {
                            errorDetail = errorData.detail;
                        }
                    } catch (_) {
                        errorDetail = (await response.text()) || errorDetail;
                    }
                    throw new Error(errorDetail);
                }
                const data: CourseSummary[] = await response.json();
                console.log("Fetched courses successfully:", data);
                setCourses(data);
            } catch (err: any) {
                console.error("Fetch courses error:", err);
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setError("Could not connect to the server.");
                } else {
                    setError(err.message || "An error occurred while fetching courses.");
                }
                setCourses([]); // Clear courses on error
            } finally {
                console.log("Fetch finished, setting loading to false.");
                setIsLoading(false);
            }
        };

        fetchCourses();

    }, [instructorId]); // Dependency array remains correct
    // --- End Fetch Courses ---


    // Navigate to the full course page
    const handleViewCourse = (courseId: string) => {
        navigate(`/courses/${courseId}`);
    };

    // Callback function for when a new course is created by the dialog
    const handleCourseCreated = () => {
        setIsRegisterDialogOpen(false); // Close the dialog
        // Re-fetch courses immediately after creation
        if (instructorId && instructorId !== "undefined") {
            console.log("Course created, re-fetching courses...");
            const fetchAgain = async () => {
                setIsLoading(true); // Show loading indicator again
                setError(null);
                const url = `http://localhost:8000/instructors/${instructorId}/courses?order_by=created_at&order_dir=desc`;
                try {
                    const response = await fetch(url);
                    if (!response.ok) throw new Error("Failed to re-fetch courses");
                    const data: CourseSummary[] = await response.json();
                    setCourses(data);
                    console.log("Courses re-fetched successfully.");
                } catch (err: any) {
                    console.error("Re-fetch failed:", err);
                    setError(err.message || "Failed to refresh courses.");
                } finally {
                    setIsLoading(false);
                }
            };
            fetchAgain(); // Call the re-fetch function
        } else {
            console.error("Cannot re-fetch, instructorId is invalid after course creation:", instructorId);
        }
    };


    // Client-side filtering based on search term
    const filteredCourses = courses.filter((course) =>
        course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.institution.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Loading State: Show only if truly loading initial data and ID is valid or potentially becoming valid
    if (isLoading && courses.length === 0 && (!error || error === "Instructor ID is missing or invalid in URL.")) {
        return <div className="text-center p-10">Loading courses... (ID: {instructorId || 'pending'})</div>;
    }

    // Error State: Show if an error occurred (and we're not actively loading)
    if (error && !isLoading) {
        return <div className="text-center text-destructive p-10">Error: {error}</div>;
    }
    // Explicit check if ID remained invalid after loading attempt
    if (!isLoading && (!instructorId || instructorId === "undefined")) {
        return <div className="text-center text-destructive p-10">Error: Invalid Instructor ID provided in URL.</div>;
    }

    // --- Main Render ---
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">My Courses</h1>
                <Dialog open={isRegisterDialogOpen} onOpenChange={setIsRegisterDialogOpen}>
                    <DialogTrigger asChild>
                        <Button disabled={!instructorId || instructorId === "undefined"}> {/* Disable if no valid ID */}
                            <Plus className="h-4 w-4 mr-2" />
                            Register New Course
                        </Button>
                    </DialogTrigger>
                    {/* Ensure instructorId is valid before rendering dialog */}
                    {instructorId && instructorId !== "undefined" && (
                        <CourseRegisterDialog
                            instructorId={instructorId}
                            onCourseCreated={handleCourseCreated}
                            onClose={() => setIsRegisterDialogOpen(false)}
                        />
                    )}
                </Dialog>
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
                <Button variant="outline">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                </Button>
            </div>

            {/* Course Grid */}
            {isLoading && courses.length > 0 && <p className="text-center text-muted-foreground">Refreshing courses...</p>} {/* Show refresh only if courses were previously loaded */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map((course) => (
                    <CourseCard
                        key={course.id}
                        course={course}
                        onViewCourse={handleViewCourse}
                    />
                ))}
            </div>

            {/* No Courses Messages */}
            {!isLoading && filteredCourses.length === 0 && courses.length > 0 && (
                <p className="text-center text-muted-foreground mt-10">
                    No courses match your search term.
                </p>
            )}
            {!isLoading && courses.length === 0 && !error && (
                <p className="text-center text-muted-foreground mt-10">
                    You haven't registered any courses yet.
                </p>
            )}
        </div>
    );
}

