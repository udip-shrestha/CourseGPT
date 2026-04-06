import type { APIClient } from "./ApiClient";

export class CourseClient {
  private baseClient: APIClient;
  constructor(baseClient: APIClient) {
    this.baseClient = baseClient;
  }
  async listInstructorCourses(
    instructorId: string,
    options?: {
      institution?: string;
      limit?: number;
      offset?: number;
      order_by?: string;
      order_dir?: "asc" | "desc";
    },
  ) {
    const query = Object.fromEntries(
      Object.entries(options || {}).filter(([_, v]) => v !== undefined),
    );
    return this.baseClient.request(
      "GET",
      `/instructors/${instructorId}/courses`,
      { query, operationId: `instructor-courses-${instructorId}` },
    );
  }

  async getCourse(courseId: string) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    return this.baseClient.request("GET", `/courses/${courseId}`, {
      operationId: `course-get-${courseId}`,
    });
  }

  async deleteCourse(courseId: string) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    return this.baseClient.request("DELETE", `/courses/${courseId}`, {
      operationId: `course-delete-${courseId}`,
    });
  }

  async createCourse(
    instructorId: string,
    params: {
      name: string;
      institution: string;
      semester_id: number;
      year: number;
    },
  ) {
    if (!instructorId) return { errorMessage: "Instructor ID is required." };
    return this.baseClient.request(
      "POST",
      `/instructors/${instructorId}/courses`,
      {
        query: params,
        isJson: false,
        operationId: `course-create-${instructorId}`,
      },
    );
  }

  async updateCourse(
    courseId: string,
    params: {
      name?: string;
      institution?: string;
      semester_id?: number;
      year?: number;
    },
  ) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    const query = Object.fromEntries(
      Object.entries(params || {}).filter(([_, v]) => v !== undefined),
    );
    return this.baseClient.request("PUT", `/courses/${courseId}`, {
      query,
      isJson: false,
      operationId: `course-update-${courseId}`,
    });
  }

  /**
   * Link an existing CourseGPT course (by internal ID) with a Canvas course identifier.
   * Used when an instructor selects a CourseGPT course to link from the Canvas flow.
   */
  async linkCanvas(
    courseId: string,
    canvasContextId: string | null,
    canvasCourseId: string,
  ) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    if (!canvasCourseId)
      return { errorMessage: "Canvas course ID is required." };
    const query = {
      course_id: courseId,
      canvas_context_id: canvasContextId || undefined,
      canvas_course_id: canvasCourseId,
    };
    return this.baseClient.request("POST", `/courses/link-canvas`, {
      query,
      isJson: false,
      operationId: `course-link-canvas-${canvasCourseId}`,
    });
  }

  async isCanvasLinked(courseId: string) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    return this.baseClient.request("GET", `/courses/${courseId}/canvas/linked`, {
      operationId: `course-canvas-linked-${courseId}`,
    });
  }

  async getCanvasFiles(courseId: string) {
    if (!courseId) return { errorMessage: "Course ID is required." };
    return this.baseClient.request("GET", `/courses/${courseId}/canvas/files`, {
      operationId: `course-canvas-files-${courseId}`,
    });
  }
}
