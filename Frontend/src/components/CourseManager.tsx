import { useState } from 'react';
import { Plus, Search, Filter, Download, Trash2, Eye } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { CourseCard } from './CourseCard';
import { FileUpload } from './FileUpload';

interface Document {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadDate: string;
  courseId: string;
}

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

export function CourseManager() {
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [newDocumentCourse, setNewDocumentCourse] = useState('');

  // Mock data
  const [courses] = useState<Course[]>([
    {
      id: '1',
      name: 'Introduction to Machine Learning',
      code: 'CS 480',
      semester: 'Fall 2024',
      studentCount: 85,
      documentCount: 12,
      lastUpdated: '2 days ago',
      color: '#3b82f6'
    },
    {
      id: '2',
      name: 'Advanced Data Science',
      code: 'CS 580',
      semester: 'Fall 2024',
      studentCount: 62,
      documentCount: 8,
      lastUpdated: '1 week ago',
      color: '#10b981'
    },
    {
      id: '3',
      name: 'Python Programming',
      code: 'CS 101',
      semester: 'Fall 2024',
      studentCount: 120,
      documentCount: 15,
      lastUpdated: '3 days ago',
      color: '#f59e0b'
    }
  ]);

  const [documents] = useState<Document[]>([
    { id: '1', name: 'Lecture 1 - Introduction.pdf', type: 'PDF', size: '2.5 MB', uploadDate: '2024-01-15', courseId: '1' },
    { id: '2', name: 'Assignment 1 Guidelines.docx', type: 'DOCX', size: '1.2 MB', uploadDate: '2024-01-14', courseId: '1' },
    { id: '3', name: 'Lab Exercise 1.py', type: 'Python', size: '15 KB', uploadDate: '2024-01-13', courseId: '1' },
    { id: '4', name: 'Syllabus.pdf', type: 'PDF', size: '800 KB', uploadDate: '2024-01-10', courseId: '2' },
    { id: '5', name: 'Dataset - Sales Data.csv', type: 'CSV', size: '5.2 MB', uploadDate: '2024-01-12', courseId: '2' }
  ]);

  const handleViewCourse = (courseId: string) => {
    setSelectedCourse(courseId);
  };

  const handleAddDocument = (courseId: string) => {
    setNewDocumentCourse(courseId);
    setIsAddDocumentOpen(true);
  };

  const handleFilesSelected = (files: File[]) => {
    console.log('Files selected:', files);
    // In a real app, you would upload these files to your backend
  };

  const selectedCourseData = courses.find(course => course.id === selectedCourse);
  const courseDocuments = documents.filter(doc => doc.courseId === selectedCourse);

  if (selectedCourse && selectedCourseData) {
    return (
        <div className=" w-full space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Button
                variant="ghost"
                onClick={() => setSelectedCourse(null)}
                className="mb-2"
              >
                ← Back to Courses
              </Button>
              <h1 className="text-2xl font-bold">{selectedCourseData.name}</h1>
              <p className="text-muted-foreground">{selectedCourseData.code} • {selectedCourseData.semester}</p>
            </div>
            <Button onClick={() => handleAddDocument(selectedCourse)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Document
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{selectedCourseData.studentCount}</div>
                <div className="text-sm text-muted-foreground">Students Enrolled</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{selectedCourseData.documentCount}</div>
                <div className="text-sm text-muted-foreground">Documents</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">4.8</div>
                <div className="text-sm text-muted-foreground">Course Rating</div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Course Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {courseDocuments.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                        <span className="text-xs font-medium">{doc.type}</span>
                      </div>
                      <div>
                        <p className="font-medium">{doc.name}</p>
                        <p className="text-sm text-muted-foreground">{doc.size} • {doc.uploadDate}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
    );
  }

  return (
      <div className=" w-full space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">My Courses</h1>
          <Dialog open={isAddDocumentOpen} onOpenChange={setIsAddDocumentOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Document
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Upload Course Documents</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="course">Select Course</Label>
                  <Select value={newDocumentCourse} onValueChange={setNewDocumentCourse}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a course" />
                    </SelectTrigger>
                    <SelectContent>
                      {courses.map((course) => (
                        <SelectItem key={course.id} value={course.id}>
                          {course.name} ({course.code})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <FileUpload onFilesSelected={handleFilesSelected} />
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsAddDocumentOpen(false)}>
                    Cancel
                  </Button>
                  <Button>Upload Documents</Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onViewCourse={handleViewCourse}
            />
          ))}
        </div>
      </div>
  );
}