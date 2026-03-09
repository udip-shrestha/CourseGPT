import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { useApiClient } from "../clients/ApiClientContext";

/**
 * Page shown when an instructor arrives from Canvas but the course isn't
 * linked yet.
 */
export function CanvasLinkPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { courseClient, apiClient } = useApiClient();

  const params = new URLSearchParams(location.search);
  const canvasId = params.get("canvas_course_id") || "";

  const [courseName, setCourseName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!canvasId) navigate("/");
  }, [canvasId, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!courseName.trim()) {
      setError("Please enter the name of the course you want to link.");
      return;
    }
    if (!apiClient.isAuthenticated()) {
      setError("You must be logged in as an instructor to link a course.");
      return;
    }
    setLoading(true);
    try {
      const { data, errorMessage } = await courseClient.linkCanvas(
          courseName,
          canvasId,
      );
      if (errorMessage) throw new Error(errorMessage);
      setSuccess("Course linked successfully. Redirecting...");
      const id = data?.course_id;
      if (id) {
        setTimeout(() => navigate(`/courses/${id}`), 1500);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to link course.");
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className="max-w-md mx-auto py-20 px-4">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-4">Connect Canvas Course</h1>
            <div className="space-y-3 text-muted-foreground text-sm leading-relaxed">
              <p>
                Please specify the corresponding CourseGPT course name below.
              </p>
              <p>
                If you haven't created the course yet, you can do so from your instructor dashboard and then revisit this page.
              </p>
            </div>
          </div>

          {error && (
              <div className="p-3 text-sm bg-destructive/10 text-destructive rounded-md border border-destructive/20">
                {error}
              </div>
          )}

          {success && (
              <div className="p-3 text-sm bg-green-500/10 text-green-600 rounded-md border border-green-500/20">
                {success}
              </div>
          )}

          {apiClient.isAuthenticated() ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="courseName" className="text-sm font-medium">
                    Course Name
                  </Label>
                  <Input
                      id="courseName"
                      className="h-11"
                      value={courseName}
                      onChange={(e) => setCourseName(e.target.value)}
                      placeholder=" course name (case-sensitive)"
                      required
                  />
                  <p className="text-[11px] text-muted-foreground italic">
                    Note: This must exactly match the course name on your dashboard.
                  </p>
                </div>
                <Button type="submit" size="lg" className="w-full" disabled={loading}>
                  {loading ? "Linking Systems..." : "Link Course"}
                </Button>
              </form>
          ) : (
              <div className="rounded-lg border border-yellow-500/20 bg-yellow-500/5 p-4 text-sm text-yellow-700">
                You need to{" "}
                <a
                    className="font-semibold underline underline-offset-4"
                    href={`/login?next=/register-course?canvas_course_id=${canvasId}`}
                >
                  log in
                </a>{" "}
                as an instructor before linking courses.
              </div>
          )}
        </div>
      </div>
  );
}