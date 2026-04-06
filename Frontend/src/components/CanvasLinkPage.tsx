import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext";
import { CanvasLinkModal } from "./CanvasLinkModal";

export function CanvasLinkPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { courseClient, apiClient } = useApiClient();

  const params = new URLSearchParams(location.search);
  const canvasCourseId = params.get("canvas_course_id") || "";
  const canvasContextId = params.get("canvas_context_id") || "";

  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selected, setSelected] = useState<any | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);

  useEffect(() => {
    if (!canvasCourseId) {
      navigate("/");
      return;
    }

    if (!apiClient.isAuthenticated()) {
      window.location.href = `/login?next=${encodeURIComponent(location.pathname + location.search)}`;
      return;
    }

    const instructorId = apiClient.getInstructorId();
    if (!instructorId) {
      setError("You must be signed in as an instructor to link courses.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const resp = await courseClient.listInstructorCourses(instructorId);
        if (resp.errorMessage) throw new Error(resp.errorMessage);
        const list = resp.data?.courses || resp.data || [];
        setCourses(list);
      } catch (e: any) {
        setError(e?.message || "Failed to load courses.");
      } finally {
        setLoading(false);
      }
    })();
  }, [
    apiClient,
    canvasCourseId,
    courseClient,
    location.pathname,
    location.search,
    navigate,
  ]);

  const handleSelect = (c: any) => {
    setSelected(c);
    setConfirmOpen(true);
  };

  const handleConfirm = async () => {
    if (!selected) return;
    setConfirmOpen(false);
    setError(null);
    try {
      const resp = await courseClient.linkCanvas(
        selected.id,
        canvasContextId || null,
        canvasCourseId,
      );
      if (resp.errorMessage) throw new Error(resp.errorMessage);
      setSuccess("Course linked — redirecting...");
      setTimeout(() => navigate(`/courses/${selected.id}`), 1200);
    } catch (e: any) {
      setError(e?.message || "Failed to link course.");
    }
  };

  if (loading) {
    return <div className="py-24 text-center">Loading courses…</div>;
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <h2 className="text-2xl font-semibold mb-2">Link a Course</h2>
      <p className="text-sm text-muted-foreground mb-6">
        Choose the CourseGPT course that matches the Canvas course you intend to
        match.
      </p>

      {error && <div className="mb-4 text-red-600">{error}</div>}
      {success && <div className="mb-4 text-green-700">{success}</div>}

      <div className="grid gap-3">
        {courses.length === 0 && <div>No courses found for your account.</div>}
        {courses.map((c) => (
          <div
            key={c.id}
            className="p-4 border rounded cursor-pointer hover:border-primary"
            onClick={() => handleSelect(c)}
          >
            <div className="font-medium">{c.name}</div>
            <div className="text-sm text-muted-foreground">
              {c.institution || c.school}
            </div>
          </div>
        ))}
      </div>

      {confirmOpen && selected && (
        <CanvasLinkModal
          course={selected}
          onConfirm={handleConfirm}
          onCancel={() => setConfirmOpen(false)}
        />
      )}
    </div>
  );
}
