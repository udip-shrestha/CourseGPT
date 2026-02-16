import { useState, useEffect, useCallback } from "react";
import { Button } from "./ui/button";

import { useParams, Routes, Route, Navigate } from "react-router-dom";

import { useApiClient } from "../clients/ApiClientContext.tsx";
import { CourseDocPage } from "./CourseDocPage";
import { CourseIntegrationsPage } from "./CourseIntegrationsPage.tsx";
import { CourseChatPage } from "./CourseChatPage.tsx";
import { CourseAnalyticsPage } from "./CourseAnalyticsPage.tsx";
import { SettingsPage } from "./CourseSettingsPage.tsx";

export function CoursePage() {
    const { courseId } = useParams();
    const { courseClient } = useApiClient();

    const [course, setCourse] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchCourse = useCallback(async () => {
        if (!courseId) return;

        setLoading(true);
        setError(null);

        const { data, errorMessage } = await courseClient.getCourse(courseId);

        if (errorMessage) {
            setError("Failed to load course: " + errorMessage);
            setCourse(null);
        } else if (data) {
            setCourse(data);
        }

        setLoading(false);
    }, [courseId, courseClient]); // Added courseClient

    useEffect(() => {
        fetchCourse();
    }, [fetchCourse]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[70vh] text-muted-foreground">
                Loading course details...
            </div>
        );
    }

    if (error || !course) {
        return (
            <div className="flex flex-col items-center justify-center h-[70vh] text-center">
                <p className="text-red-600 font-semibold mb-2">
                    Course not found or failed to load.
                </p>
                {error && (
                    <p className="text-sm text-muted-foreground mb-4 max-w-sm">{error}</p>
                )}
                <Button variant="outline" onClick={fetchCourse}>
                    Retry
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <div className="text-center sm:text-left">

                    {/* <Button
                        variant="ghost"
                        onClick={() =>
                            // This uses the instructor_id from the fetched course data
                            navigate(`/instructors/${course.instructor_id}/courses`)
                        }
                        className="mb-2 -ml-4" // Use negative margin to align
                    >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        Back to Courses
                    </Button> */}

                    <h1 className="text-2xl sm:text-3xl font-bold break-words">
                        {course.name}
                    </h1>
                    <p className="text-muted-foreground text-sm sm:text-base">
                        {course.institution} • {course.semester_name || "Unknown"}{" "}
                        {course.year}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                        Instructor: {course.instructor_name} ({course.instructor_email})
                    </p>
                </div>
            </div>

            {/* Nested Routes */}
            <Routes>
                <Route index element={<CourseDocPage course={course} />} />
                <Route path="chats" element={<CourseChatPage course={course} />} />
                <Route path="integrations" element={<CourseIntegrationsPage course={course} />}/>
                <Route path="analytics" element={<CourseAnalyticsPage course={course} />} />
                <Route path="settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="." replace />} />
            </Routes>
        </div>
    );
}