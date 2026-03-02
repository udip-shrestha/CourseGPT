import type { APIClient } from "./ApiClient";

export class CanvasStudentClient {
  private baseClient: APIClient;
  constructor(baseClient: APIClient) {
    this.baseClient = baseClient;
  }

  /**
   * Register a student in a course. If canvasUserId is supplied the record will
   * be linked for LTI launches.
   */
  async register(name: string | null, courseId: string, canvasUserId?: string) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    const query: Record<string, string> = { course_id: courseId };
    if (name !== null && name !== undefined) query.name = name;
    if (canvasUserId) query.canvas_user_id = canvasUserId;
    return this.baseClient.request("POST", "/students/register", {
      query,
      isJson: false,
      operationId: `student-register-${courseId}`,
    });
  }

  /**
   * Check whether a given canvas user is already enrolled in a course.
   */
  async lookupByCanvas(canvasUserId: string, courseId: string) {
    if (!canvasUserId || !courseId)
      return { errorMessage: "Canvas ID and course ID required." };
    const query = { canvas_user_id: canvasUserId, course_id: courseId };
    return this.baseClient.request("GET", "/students/is_registered_canvas", {
      query,
      operationId: `student-lookup-canvas-${canvasUserId}`,
    });
  }
}
