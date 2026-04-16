import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Search, Filter, Plus, AlertCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { CourseCard } from "./CourseCard";
import { CourseRegisterDialog } from "./CourseRegisterDialog";
import { Dialog, DialogTrigger } from "./ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";

import { useApiClient } from "../clients/ApiClientContext";

export interface CourseSummary {
    id: string;
    instructor_id: string;
    name: string;
    institution: string;
    semester_id: number;
    year: number;
    created_at: string;
    status?: string;
}

function semesterIdToString(id: number | undefined): string {
    if (id === undefined) return "N/A";
    switch (id) {
        case 1: return "Spring";
        case 2: return "Summer";
        case 3: return "Fall";
        default: return "Unknown";
    }
}

export function InstructorCourses() {
    const { instructorId } = useParams<{ instructorId: string }>();
    console.log("InstructorCourses mounted with instructorId:", instructorId);

    const navigate = useNavigate();
    // --- 2. INITIALIZE the courseClient ---
    const { courseClient } = useApiClient();

    const [searchTerm, setSearchTerm] = useState("");
    const [courses, setCourses] = useState<CourseSummary[]>([]);
    const [total, setTotal] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null);
    const [isRegisterDialogOpen, setIsRegisterDialogOpen] = useState(false);


    const fetchCourses = useCallback(async () => {
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


        const { data, errorMessage } = await courseClient.listCourses({
            instructor_id: instructorId,
            order_by: "created_at",
            order_dir: "desc"
        });

        if (errorMessage) {
            console.error("Fetch courses error:", errorMessage);
            if (errorMessage.includes("Failed to fetch")) { // Check for network error
                setError("Could not connect to the server.");
            } else {
                setError(errorMessage || "An error occurred while fetching courses.");
            }
            setCourses([]);
            setTotal(0);
        } else if (data) {
            console.log("Fetched courses successfully:", data);
            setCourses(data.courses || []); // Set courses from the 'courses' property
            setTotal(data.total || 0);     // Set total from the 'total' property
        }

        console.log("Fetch finished, setting loading to false.");
        setIsLoading(false);

    }, [instructorId, courseClient]); // Added courseClient dependency

    useEffect(() => {
        fetchCourses();
    }, [fetchCourses]);



    const handleDeleteCourse = async (courseId: string) => {
        console.log(`Attempting to delete course ${courseId}`);
        setDeleteError(null);
        try {
            // Use the courseClient to delete
            const { errorMessage } = await courseClient.deleteCourse(courseId);

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            console.log(`Course ${courseId} deleted successfully.`);
            await fetchCourses(); // Refresh the course list
            return; // Success

        } catch (err: any) {
            console.error("Failed to delete course:", err);
            let userError = err.message || "An unexpected error occurred during deletion.";
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                userError = "Could not connect to the server. Please ensure it's running.";
            }
            setDeleteError(userError);
            throw err;
        }
    };


    const handleViewCourse = (course: CourseSummary) => {
        if (course.status?.toLowerCase() !== "enabled") return;

        console.log("Navigating to view course:", course.name, course.status);
        navigate(`/courses/${course.id}`, {
            state: {
                courseName: course.name,
                institution: course.institution,
                semester: semesterIdToString(course.semester_id),
                year: course.year,
                courseCode: `CS ${course.semester_id}01`
            }
        });
    };

    const handleCourseCreated = () => {
        setIsRegisterDialogOpen(false);
        fetchCourses(); // Re-fetch the course list
    };


    const handleCourseUpdated = () => {
        fetchCourses(); // Re-fetch the course list
    }

    const filteredCourses = courses.filter((course) =>
        course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.institution.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (isLoading && courses.length === 0) {
        return <div className="text-center p-10">Loading courses... (ID: {instructorId || 'pending'})</div>;
    }

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
                        onViewCourse={() => handleViewCourse(course)}
                        onDelete={() => handleDeleteCourse(course.id)}
                        // --- 5. PASS THE PROP ---
                        onCourseUpdated={handleCourseUpdated}
                    />
                ))}
            </div>

            {!isLoading && filteredCourses.length === 0 && courses.length > 0 && (
                <p className="text-center text-muted-foreground mt-10">
                    No courses match your search term.
                </p>
            )}
            {!isLoading && total === 0 && !error && (
                <p className="text-center text-muted-foreground mt-10">
                    You haven't registered any courses yet.
                </p>
            )}
        </div>
    );
}