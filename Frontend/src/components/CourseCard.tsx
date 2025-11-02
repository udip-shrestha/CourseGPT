import { BookOpen, Calendar, Building } from 'lucide-react'; // Changed icons
import { Card, CardContent, CardHeader } from './ui/card';

import { Button } from './ui/button';
import type {CourseSummary} from './InstructorCourses'; // Import the interface reflecting API data


// Interface for props using the API data structure
interface CourseCardProps {
    course: CourseSummary;
    onViewCourse: (courseId: string) => void;
}

// Helper to convert semester ID to string (Adjust mapping if needed based on your backend)
function semesterIdToString(id: number): string {
    switch (id) {
        case 1: return "Spring";
        case 2: return "Summer";
        case 3: return "Fall";
        case 4: return "Fall"; // Handling the '4' seen in Swagger example
        default: return "Unknown";
    }
}

export function CourseCard({ course, onViewCourse }: CourseCardProps) {
    const semesterString = semesterIdToString(course.semester_id);

    return (
        // You can add className="dark" here if you want dark cards on a light background
        <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
                {/* Updated Header Content */}
                <div className="space-y-1">
                    <h3 className="font-semibold leading-tight text-lg">{course.name}</h3>
                    {/* Display Institution */}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Building className="h-4 w-4" />
                        <span>{course.institution}</span>
                    </div>
                    {/* Display Semester and Year */}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>{semesterString} {course.year}</span>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="pt-2">
                {/* Removed old stats grid (studentCount, documentCount, lastUpdated) */}
                {/* View Course Button */}
                <Button
                    onClick={() => onViewCourse(course.id)}
                    className="w-full mt-4" // Added margin-top for spacing
                    variant="outline"
                >
                    <BookOpen className="h-4 w-4 mr-2" />
                    View Course
                </Button>
            </CardContent>
        </Card>
    );
}

