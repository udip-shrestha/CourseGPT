import { useParams, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useApiClient } from "../ApiClientContext";
import { NotFoundPage } from "./NotFoundPage";
import { CourseDocPage } from "./CourseDocPage";

export function CoursePage() {
  const { courseId } = useParams();
  const apiClient = useApiClient();

  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCourse() {
      if (!courseId) return;
  
      setLoading(true);
      setError(null);
  
      let courses: any[] = [];
  
      try {
        const instructorId = apiClient.getInstructorId();
        if (!instructorId) throw new Error("No instructor ID found");
  
        // Fetch instructor's courses
        const { data, errorMessage } = await apiClient.listInstructorCourses(instructorId, {
          limit: 5,
          order_by: "created_at",
          order_dir: "desc",
        });

        courses = data?.courses ?? [];
  
        if (errorMessage || courses.length === 0)
          throw new Error("API call failed or no courses found");
      } catch (err) {
        console.error("Fetch failed:", err);
        courses = mockCourses; // fallback ensures finally always has value
      } finally {
        const course = courses.find((c) => c.id === courseId) || courses[0];
  
        setCourse(course);
        setLoading(false);
      }
    }
  
    fetchCourse();
  }, [courseId, apiClient]);
  
  
  // === Render states ===
  if (loading) return <p className="text-center mt-10">Loading course...</p>;
  if (error) return <p className="text-center text-destructive">{error}</p>;
  if (!course) return <p className="text-center text-muted">Course not found.</p>;

  // === Nested routes ===
  return (
    <div className="container mx-auto px-4 py-6 space-y-8">
      <Routes>
        <Route index element={<CourseDocPage course={course} />} />
        <Route path="chat" element={<NotFoundPage />} />
        <Route path="integrations" element={<NotFoundPage />} />
        <Route path="settings" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="." replace />} />
      </Routes>
    </div>
  );
}

// Temporary mock until backend integration
const mockCourses = [
  { id: "1", name: "Intro to ML", code: "CS480", semester: "Fall 2024", studentCount: 85, documentCount: 12 },
  { id: "2", name: "Advanced DS", code: "CS580", semester: "Fall 2024", studentCount: 62, documentCount: 8 },
  { id: "3", name: "Python 101", code: "CS101", semester: "Fall 2024", studentCount: 120, documentCount: 15 },
];
