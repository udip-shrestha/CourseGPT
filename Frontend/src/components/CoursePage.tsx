import { useState, useEffect, useCallback } from "react";
import { Button } from "./ui/button";

import {
  useParams,
  Routes,
  Route,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

import { useApiClient } from "../clients/ApiClientContext.tsx";
import { CourseDocPage } from "./CourseDocPage";
import { CourseIntegrationsPage } from "./CourseIntegrationsPage.tsx";
import { CourseChatPage } from "./CourseChatPage.tsx";
import { SettingsPage } from "./CourseSettingsPage.tsx";
import { CourseAnalyticsPage } from "./CourseAnalyticsPage.tsx";
import { CourseAllQuestionsPage } from "./CourseAllQuestionsPage";

export function CoursePage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { courseClient, canvasStudentClient } = useApiClient();

  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // student registration/query params
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const roleParam = searchParams.get("role");
  const needsReg = searchParams.get("needs_registration");
  const canvasUserId = searchParams.get("canvas_user_id");
  const [showStudentReg, setShowStudentReg] = useState(false);
  const [studentName, setStudentName] = useState("");
  const [studentError, setStudentError] = useState<string | null>(null);
  const [studentLoading, setStudentLoading] = useState(false);

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

  // If the launch indicated that the student needs registration, prompt now
  useEffect(() => {
    if (roleParam === "student" && needsReg === "1" && canvasUserId) {
      setShowStudentReg(true);
    }
  }, [roleParam, needsReg, canvasUserId]);

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

  // ------- student registration UI -------
  const handleStudentRegister = async () => {
    if (!canvasUserId) return;
    setStudentError(null);
    setStudentLoading(true);
    try {
      const { data, errorMessage } = await canvasStudentClient.register(
        studentName || null,
        courseId || "",
        canvasUserId,
      );
      if (errorMessage) throw new Error(errorMessage);
      // registration succeeded, close dialog and navigate to clean url
      if (data) setShowStudentReg(false);
      navigate(`/courses/${courseId}/chats?role=student`);
    } catch (err: any) {
      setStudentError(err.message || "Registration failed");
    } finally {
      setStudentLoading(false);
    }
  };

  const registrationDialog = showStudentReg ? (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-70">
      <div className="bg-white dark:bg-black p-6 rounded shadow max-w-sm w-full">
        <h2 className="text-lg font-semibold mb-4">Student Registration</h2>
        <p className="text-sm mb-2">
          This course requires registration to proceed. Please provide your name
          and click confirm.
        </p>
        {studentError && (
          <p className="text-destructive mb-2">{studentError}</p>
        )}
        <input
          className="w-full border px-2 py-1 mb-4"
          placeholder="Your full name"
          value={studentName}
          onChange={(e) => setStudentName(e.target.value)}
        />
        <div className="flex justify-end gap-2">
          <Button
            onClick={() => setShowStudentReg(false)}
            disabled={studentLoading}
            variant="outline"
          >
            Cancel
          </Button>
          <Button onClick={handleStudentRegister} disabled={studentLoading}>
            {studentLoading ? "Registering..." : "Confirm"}
          </Button>
        </div>
      </div>
    </div>
  ) : null;

  return (
    <div className="space-y-6">
      {registrationDialog}
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
        <Route
          path="questions"
          element={<CourseAllQuestionsPage course={course} />}
        />
        <Route
          path="integrations"
          element={<CourseIntegrationsPage course={course} />}
        />
        <Route
          path="analytics"
          element={<CourseAnalyticsPage course={course} />}
        />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="." replace />} />
      </Routes>
    </div>
  );
}
