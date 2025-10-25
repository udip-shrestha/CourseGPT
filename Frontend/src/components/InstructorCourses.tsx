import { useState } from "react";
import { Search, Filter } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { CourseCard } from "./CourseCard";
import { useNavigate } from "react-router-dom";

interface Course {
  id: string;
  name: string;
  code: string;
  semester: string;
  studentCount: number;
  documentCount: number;
  lastUpdated: string;
  color: string;
}

export function InstructorCourses() {
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  // Mock data
  const [courses] = useState<Course[]>([
    {
      id: "1",
      name: "Introduction to Machine Learning",
      code: "CS 480",
      semester: "Fall 2024",
      studentCount: 85,
      documentCount: 12,
      lastUpdated: "2 days ago",
      color: "#3b82f6",
    },
    {
      id: "2",
      name: "Advanced Data Science",
      code: "CS 580",
      semester: "Fall 2024",
      studentCount: 62,
      documentCount: 8,
      lastUpdated: "1 week ago",
      color: "#10b981",
    },
    {
      id: "3",
      name: "Python Programming",
      code: "CS 101",
      semester: "Fall 2024",
      studentCount: 120,
      documentCount: 15,
      lastUpdated: "3 days ago",
      color: "#f59e0b",
    },
  ]);

  const handleViewCourse = (courseId: string) => {
    navigate(`/courses/${courseId}`);
  };

  // Optional: filter courses by search term
  const filteredCourses = courses.filter((course) =>
    course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">My Courses</h1>
        </div>

        {/* Search + Filter */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
        </div>

        {/* Course Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onViewCourse={handleViewCourse}
            />
          ))}
        </div>

        {filteredCourses.length === 0 && (
          <p className="text-center text-muted-foreground mt-10">
            No courses found.
          </p>
        )}
      </div>
    </div>
  );
}
