import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { useApiClient } from "../clients/ApiClientContext";

/**
 * Page shown when an instructor arrives from Canvas but the course isn't
 * linked yet.  The Canvas redirect attaches a `canvas_course_id` query
 * parameter; this page asks the user to enter the internal course name to
 * associate and then submits the link request.
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
        // if there is no canvas id, redirect to home
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
                canvasId
            );
            if (errorMessage) throw new Error(errorMessage);
            setSuccess("Course linked successfully. Redirecting...");
            // data.course_id should contain the internal id
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
        <div className="max-w-md mx-auto py-12">
            <h1 className="text-2xl font-semibold mb-4">Link Canvas Course</h1>
            <p className="mb-4">
                We received a Canvas course identifier{' '}
                <code className="font-mono bg-muted px-1 py-0.5 rounded">
                    {canvasId}
                </code>.
                Please specify the corresponding CourseGPT course name below. If you
                haven't created the course yet, you can do so from your instructor
                dashboard and then revisit this page.
            </p>
            {error && <p className="text-destructive mb-2">{error}</p>}
            {success && <p className="text-green-600 mb-2">{success}</p>}
            {apiClient.isAuthenticated() ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid gap-2">
                        <Label htmlFor="courseName">Course Name</Label>
                        <Input
                            id="courseName"
                            value={courseName}
                            onChange={(e) => setCourseName(e.target.value)}
                            placeholder="Exact course name (case‑sensitive)"
                            required
                        />
                    </div>
                    <Button type="submit" disabled={loading}>
                        {loading ? "Linking..." : "Link Course"}
                    </Button>
                </form>
            ) : (
                <p className="text-sm text-muted-foreground">
                    You need to <a className="text-blue-600 underline" href={`/login?next=/register-course?canvas_course_id=${canvasId}`}>log in</a> as an instructor before linking courses.
                </p>
            )}
        </div>
    );
}
