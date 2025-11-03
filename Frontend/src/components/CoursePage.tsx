import { useParams } from "react-router-dom";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Plus, Eye, Download, Trash2 } from "lucide-react";
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { FileUpload } from "./FileUpload";

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

export function CoursePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);

  const [documents] = useState<Document[]>([
    { id: "1", name: "Lecture 1 - Introduction.pdf", type: "PDF", size: "2.5 MB", uploadDate: "2024-01-15", courseId: "1" },
    { id: "2", name: "Assignment 1 Guidelines.docx", type: "DOCX", size: "1.2 MB", uploadDate: "2024-01-14", courseId: "1" },
    { id: "3", name: "Lab Exercise 1.py", type: "Python", size: "15 KB", uploadDate: "2024-01-13", courseId: "1" },
    { id: "4", name: "Syllabus.pdf", type: "PDF", size: "800 KB", uploadDate: "2024-01-10", courseId: "2" },
    { id: "5", name: "Dataset - Sales Data.csv", type: "CSV", size: "5.2 MB", uploadDate: "2024-01-12", courseId: "2" },
    { id: "6", name: "Lecture 1 - Basics.ipynb", type: "Notebook", size: "450 KB", uploadDate: "2024-01-09", courseId: "3" },
    { id: "7", name: "Assignment 1.pdf", type: "PDF", size: "2.1 MB", uploadDate: "2024-01-10", courseId: "3" },
    { id: "8", name: "Practice Problems.zip", type: "ZIP", size: "3.4 MB", uploadDate: "2024-01-11", courseId: "3" },
  ]);

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

  const selectedCourse = courses.find((c) => c.id === courseId);
  const courseDocuments = documents.filter((doc) => doc.courseId === courseId);

  if (!selectedCourse) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Course not found.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Course header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="text-center sm:text-left">
          <h1 className="text-2xl sm:text-3xl font-bold break-words">
            {selectedCourse.name}
          </h1>
          <p className="text-muted-foreground text-sm sm:text-base">
            {selectedCourse.code} • {selectedCourse.semester}
          </p>
        </div>
        <div className="flex justify-center sm:justify-end">
          <Button className="w-full sm:w-auto" onClick={() => setIsAddDocumentOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Document
          </Button>
        </div>
      </div>

      {/* Course Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <Card className="text-center">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{selectedCourse.studentCount}</div>
            <div className="text-sm text-muted-foreground">Students Enrolled</div>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{selectedCourse.documentCount}</div>
            <div className="text-sm text-muted-foreground">Documents</div>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">4.8</div>
            <div className="text-sm text-muted-foreground">Course Rating</div>
          </CardContent>
        </Card>
      </div>

      {/* Course Documents */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg sm:text-xl text-center sm:text-left">
            Course Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {courseDocuments.map((doc) => (
              <div
                key={doc.id}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-medium">{doc.type}</span>
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-sm sm:text-base truncate">
                      {doc.name}
                    </p>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      {doc.size} • {doc.uploadDate}
                    </p>
                  </div>
                </div>

                <div className="flex justify-end sm:justify-start gap-1 sm:gap-2">
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

      {/* Add Document Dialog */}
      <Dialog open={isAddDocumentOpen} onOpenChange={setIsAddDocumentOpen}>
        <DialogContent className="max-w-md sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload Documents for {selectedCourse.name}</DialogTitle>
          </DialogHeader>
          <FileUpload onFilesSelected={(files) => console.log(files)} />
          <div className="flex flex-col sm:flex-row justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setIsAddDocumentOpen(false)}
              className="w-full sm:w-auto"
            >
              Cancel
            </Button>
            <Button className="w-full sm:w-auto">Upload</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
