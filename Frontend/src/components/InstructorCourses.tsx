import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Search, Filter, Plus, AlertCircle } from "lucide-react"; // Added AlertCircle
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { CourseCard } from "./CourseCard";
import { CourseRegisterDialog } from "./CourseRegisterDialog";
import { Dialog, DialogTrigger } from "./ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert"; // Added Alert

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
    const { instructorId } = useParams<{ instructorId: string }>();
    console.log("InstructorCourses mounted with instructorId:", instructorId);

    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState("");
    const [courses, setCourses] = useState<CourseSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null); // State for delete errors
    const [isRegisterDialogOpen, setIsRegisterDialogOpen] = useState(false);

    // --- Fetch Courses Effect ---
    const fetchCourses = async () => {
        // Clear delete error on refresh
        setDeleteError(null);

        if (!instructorId || instructorId === "undefined") {
            console.error("GUARD: Instructor ID is missing or invalid, stopping fetch.", instructorId);
            setError("Instructor ID is missing or invalid in URL.");
            setIsLoading(false);
            return;
        }

        console.log("GUARD PASSED: Proceeding with fetch for instructorId:", instructorId);
        setIsLoading(true);
        setError(null);

        const url = `http://localhost:8000/instructors/${instructorId}/courses?order_by=created_at&order_dir=desc`; // Added sorting
        console.log("Fetching courses from:", url);

        try {
            const response = await fetch(url);
            if (!response.ok) {
                let errorDetail = `Failed to fetch courses (Status: ${response.status})`;
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
            setCourses([]);
        } finally {
            console.log("Fetch finished, setting loading to false.");
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchCourses();
    }, [instructorId]);
    // --- End Fetch Courses ---

    // --- Delete Course Handler ---
    const handleDeleteCourse = async (courseId: string) => {
        console.log(`Attempting to delete course ${courseId}`);
        setDeleteError(null); // Clear previous delete errors
        try {
            const response = await fetch(`http://localhost:8000/courses/${courseId}`, {
                method: 'DELETE',
                headers: { 'accept': '*/*' } // As per Swagger
            });

            // 204 No Content is a successful deletion
            if (response.status === 204) {
                console.log(`Course ${courseId} deleted successfully.`);
                // Refresh the course list
                await fetchCourses();
                return; // Success
            }

            // Handle other non-ok responses
            if (!response.ok) {
                let errorDetail = `Failed to delete course (Status: ${response.status})`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                } catch (_) {}
                throw new Error(errorDetail);
            }

        } catch (err: any) {
            console.error("Failed to delete course:", err);
            let userError = err.message || "An unexpected error occurred during deletion.";
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                userError = "Could not connect to the server. Please ensure it's running.";
            }
            // Set the delete error to display it in an alert
            setDeleteError(userError);

            // Re-throw the error to be caught by the card's local handler
            throw err;
        }
    };
    // --- End Delete Course Handler ---

    const handleViewCourse = (courseId: string) => {
        navigate(`/courses/${courseId}`);
    };

    const handleCourseCreated = () => {
        setIsRegisterDialogOpen(false);
        fetchCourses(); // Re-fetch the course list
    };

    const filteredCourses = courses.filter((course) =>
        course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.institution.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (isLoading && courses.length === 0) {
        return <div className="text-center p-10">Loading courses... (ID: {instructorId || 'pending'})</div>;
    }

    // Display general fetch error only
    if (error && !isLoading) {
        return <div className="text-center text-destructive p-10">Error: {error}</div>;
    }
    if (!isLoading && (!instructorId || instructorId === "undefined")) {
        return <div className="text-center text-destructive p-10">Error: Invalid Instructor ID provided in URL.</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">My Courses</h1>
                <Dialog open={isRegisterDialogOpen} onOpenChange={setIsRegisterDialogOpen}>
                    <DialogTrigger asChild>
                        <Button disabled={!instructorId || instructorId === "undefined"}>
                            <Plus className="h-4 w-4 mr-2" />
                            Register New Course
                        </Button>
                    </DialogTrigger>
                    {instructorId && instructorId !== "undefined" && (
                        <CourseRegisterDialog
                            instructorId={instructorId}
                            onCourseCreated={handleCourseCreated}
                            onClose={() => setIsRegisterDialogOpen(false)}
                        />
                    )}
                </Dialog>
            </div>

            {/* Display Delete Error Alert if it exists */}
            {deleteError && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Delete Error</AlertTitle>
                    <AlertDescription>{deleteError}</AlertDescription>
                </Alert>
            )}

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

            {isLoading && courses.length > 0 && <p className="text-center text-muted-foreground">Refreshing courses...</p>}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map((course) => (
                    <CourseCard
                        key={course.id}
                        course={course}
                        onViewCourse={handleViewCourse}
                        // Pass the delete handler to each card
                        onDelete={() => handleDeleteCourse(course.id)}
                    />
                ))}
            </div>

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

