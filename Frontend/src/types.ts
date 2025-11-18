/**
 * Defines the basic course structure, used in the course list.
 */
export interface CourseSummary {
    id: string;
    instructor_id: string;
    name: string;
    institution: string;
    semester_id: number;
    year: number;
    created_at: string;
}

/**
 * Defines the detailed course structure, used in the course detail page.
 * Extends CourseSummary to include additional details.
 */
export interface CourseDetail extends CourseSummary {
    code?: string;
    semester_name?: string;
    instructor_name?: string;
    instructor_email?: string;
    studentCount?: number;
    documentCount?: number;
}