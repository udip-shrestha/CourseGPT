import { useCallback, useEffect, useState } from "react";
import { BookOpen, RefreshCw } from "lucide-react";

import { useApiClient } from "../clients/ApiClientContext";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "./ui/card";

interface CourseSummary {
  id: string;
  instructor_id: string;
  instructor_name?: string;
  instructor_email?: string;
  name: string;
  institution: string;
  semester_id: number;
  semester_name?: string;
  year: number;
  created_at: string;
  status?: "PENDING" | "ENABLED" | "DISABLED";
  canvas_course_id?: string | null;
  canvas_context_id?: string | null;
}

export function AdminCoursesPage() {
  const { courseClient, adminClient } = useApiClient();

  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<"ALL" | "PENDING" | "ENABLED" | "DISABLED">("ALL");
  const [institutionFilter, setInstitutionFilter] = useState("");
  const [instructorEmailFilter, setInstructorEmailFilter] = useState("");

  const [updatingCourseId, setUpdatingCourseId] = useState<string | null>(null);

  const fetchCourses = useCallback(
    async (showRefreshSpinner = false) => {
      if (showRefreshSpinner) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      const { data, errorMessage } = await courseClient.listCourses({
        instructor_email: instructorEmailFilter.trim() || undefined,
        institution: institutionFilter.trim() || undefined,
        status: statusFilter === "ALL" ? undefined : statusFilter,
        limit: 500,
        offset: 0,
        order_by: "created_at",
        order_dir: "desc",
      });

      if (errorMessage) {
        setCourses([]);
        setError(errorMessage);
      } else if (data) {
        setCourses(data.courses || data || []);
      } else {
        setCourses([]);
      }

      setIsLoading(false);
      setIsRefreshing(false);
    },
    [courseClient, institutionFilter, statusFilter, instructorEmailFilter],
  );

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  async function handleToggleCourse(course: CourseSummary) {
    const currentlyEnabled = course.status === "ENABLED";
    const nextEnabled = !currentlyEnabled;

    setUpdatingCourseId(course.id);
    setError(null);

    const { errorMessage } = await adminClient.updateCourseStatus(
      course.id,
      nextEnabled,
    );

    if (errorMessage) {
      setError(errorMessage);
      setUpdatingCourseId(null);
      return;
    }

    await fetchCourses(true);
    setUpdatingCourseId(null);
  }

  function getStatusClasses(status?: string) {
    switch (status) {
      case "ENABLED":
        return "bg-green-100 text-green-700 border-green-200";
      case "DISABLED":
        return "bg-red-100 text-red-700 border-red-200";
      default:
        return "bg-yellow-100 text-yellow-700 border-yellow-200";
    }
  }

  function getCanvasLinkClasses(course: CourseSummary) {
    return course.canvas_course_id || course.canvas_context_id
      ? "bg-blue-100 text-blue-700 border-blue-200"
      : "bg-gray-100 text-gray-600 border-gray-200";
  }

  function getCanvasLinkLabel(course: CourseSummary) {
    return course.canvas_course_id || course.canvas_context_id
      ? "Canvas Linked"
      : "Not Linked";
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BookOpen className="h-7 w-7" />
            Admin Courses
          </h1>
          <p className="text-muted-foreground mt-1">
            View all courses and enable or disable them.
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => fetchCourses(true)}
          disabled={isLoading || isRefreshing}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Filter courses by status, institution, or instructor email.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Status</label>
              <select
                value={statusFilter}
                onChange={(e) =>
                  setStatusFilter(
                    e.target.value as
                      | "ALL"
                      | "PENDING"
                      | "ENABLED"
                      | "DISABLED",
                  )
                }
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              >
                <option value="ALL">All statuses</option>
                <option value="PENDING">Pending</option>
                <option value="ENABLED">Enabled</option>
                <option value="DISABLED">Disabled</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">
                Institution
              </label>
              <input
                type="text"
                value={institutionFilter}
                onChange={(e) => setInstitutionFilter(e.target.value)}
                placeholder="Filter by institution..."
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">
                Instructor Email
              </label>
              <input
                type="text"
                value={instructorEmailFilter}
                onChange={(e) => setInstructorEmailFilter(e.target.value)}
                placeholder="Filter by instructor email..."
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="py-16 text-center text-muted-foreground">
              Loading courses...
            </div>
          ) : error ? (
            <div className="py-12 text-center">
              <p className="text-destructive font-medium mb-2">
                Failed to load courses.
              </p>
              <p className="text-sm text-muted-foreground mb-4">{error}</p>
              <Button variant="outline" onClick={() => fetchCourses(true)}>
                Retry
              </Button>
            </div>
          ) : courses.length === 0 ? (
            <div className="py-16 text-center">
              <p className="font-medium">No courses found.</p>
              <p className="text-sm text-muted-foreground mt-1">
                Try changing your filters.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {courses.map((course) => {
                const isEnabled = course.status === "ENABLED";
                const isUpdating = updatingCourseId === course.id;

                return (
                  <div
                    key={course.id}
                    className="border rounded-lg p-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-semibold text-lg">{course.name}</h3>
                        <span
                          className={`text-xs px-2 py-1 rounded-full border ${getStatusClasses(course.status)}`}
                        >
                          {course.status || "PENDING"}
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded-full border ${getCanvasLinkClasses(course)}`}
                        >
                          {getCanvasLinkLabel(course)}
                        </span>
                      </div>

                      <p className="text-sm text-muted-foreground">
                        Instructor: {course.instructor_name || "Unknown"}
                      </p>

                      <p className="text-sm text-muted-foreground">
                        Email: {course.instructor_email || "Unknown"}
                      </p>

                      <p className="text-sm text-muted-foreground">
                        {course.institution} •{" "}
                        {course.semester_name || "Unknown"} {course.year}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        Created: {new Date(course.created_at).toLocaleString()}
                      </p>

                      {(course.canvas_course_id || course.canvas_context_id) && (
                        <p className="text-xs text-muted-foreground">
                          Canvas Course ID: {course.canvas_course_id || "N/A"} •
                          Canvas Context ID: {course.canvas_context_id || "N/A"}
                        </p>
                      )}
                    </div>

                    <div className="flex justify-start md:justify-end">
                      <Button
                        variant={isEnabled ? "destructive" : "default"}
                        onClick={() => handleToggleCourse(course)}
                        disabled={isUpdating}
                      >
                        {isUpdating
                          ? "Updating..."
                          : isEnabled
                            ? "Disable Course"
                            : "Enable Course"}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}