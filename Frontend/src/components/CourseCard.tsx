import { BookOpen, Users, FileText, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

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

interface CourseCardProps {
  course: Course;
  onViewCourse: (courseId: string) => void;
}

export function CourseCard({ course, onViewCourse }: CourseCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: course.color }}
            />
            <Badge variant="secondary" className="text-xs">
              {course.code}
            </Badge>
          </div>
          <h3 className="font-medium leading-tight">{course.name}</h3>
          <p className="text-sm text-muted-foreground">{course.semester}</p>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0 space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span>{course.studentCount} students</span>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span>{course.documentCount} documents</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>Updated {course.lastUpdated}</span>
        </div>
        
        <Button 
          onClick={() => onViewCourse(course.id)}
          className="w-full"
          variant="outline"
        >
          <BookOpen className="h-4 w-4 mr-2" />
          View Course
        </Button>
      </CardContent>
    </Card>
  );
}