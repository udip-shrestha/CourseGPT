import { useParams } from "react-router-dom"; // Removed useNavigate
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Plus, Eye, Download, Trash2 } from "lucide-react";
import { useState, useEffect } from "react"; // Added useEffect
// --- FIX: Removed unused DialogTrigger ---
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { FileUpload } from "./FileUpload";
// Removed unused Badge import

// --- Define Interfaces ---
// Interface for the detailed course data (adjust based on actual GET /courses/{id} response)
interface CourseDetail {
    id: string;
    instructor_id: string; // Assuming API returns this
    name: string;
    institution?: string; // Add if API returns it
    semester_id?: number; // Add if API returns it
    year?: number;       // Add if API returns it
    code?: string;       // Keep if API returns it
    semester?: string;   // Keep if API returns it (or derive from semester_id)
    studentCount?: number; // Placeholder - Fetch separately if needed
    documentCount?: number;// Placeholder - Fetch separately if needed
    // created_at?: string; // Add if needed
}

// Interface for document data (adjust based on actual GET /courses/{id}/documents response)
interface Document {
    id: string;
    file_name: string;
    uploaded_at: string;
    // --- FIX: Add the properties created in the .map() function ---
    name: string;       // Added from mapping doc.file_name
    uploadDate: string; // Added from mapping new Date(...)
    // -----------------------------------------------------------
    type?: string;
    size?: string;
}
// --- End Interfaces ---

// --- Helper Functions ---
// Helper to convert semester ID to string (Ensure consistency)
function semesterIdToString(id: number | undefined): string {
    if (id === undefined) return "N/A";
    switch (id) {
        case 1: return "Spring";
        case 2: return "Summer";
        case 3: return "Fall";
        case 4: return "Fall";
        default: return "Unknown";
    }
}
// --- End Helper Functions ---


export function CoursePage() {
    const { courseId } = useParams<{ courseId: string }>();
    // const navigate = useNavigate(); // Removed this line

    // --- State ---
    const [course, setCourse] = useState<CourseDetail | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isLoadingCourse, setIsLoadingCourse] = useState(true);
    const [isLoadingDocs, setIsLoadingDocs] = useState(true);
    const [courseError, setCourseError] = useState<string | null>(null);
    const [docsError, setDocsError] = useState<string | null>(null);
    const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);
    // --- End State ---


    // --- Fetch Course Details ---
    useEffect(() => {
        if (!courseId) {
            setCourseError("Course ID not found in URL.");
            setIsLoadingCourse(false);
            return;
        }
        const fetchCourseDetails = async () => {
            setIsLoadingCourse(true);
            setCourseError(null);
            try {
                // --- TODO: Replace with ACTUAL GET /courses/{courseId} endpoint ---
                console.warn(`Fetching course details for ${courseId} - using placeholder`);
                // const response = await fetch(`http://localhost:8000/courses/${courseId}`);
                // if (!response.ok) throw new Error('Failed to fetch course details');
                // const data: CourseDetail = await response.json();

                // --- MOCK DATA FOR NOW ---
                await new Promise(res => setTimeout(res, 500)); // Simulate fetch time
                // Make mock data slightly more consistent with potential API
                const mockData: CourseDetail = {
                    id: courseId,
                    instructor_id: "mock-instructor-id", // Needed for Back button potentially
                    name: `Course ${courseId} Details`, // Example Name
                    institution: "Mock University",
                    semester_id: 3, // Fall
                    year: 2024,
                    code: `CS ${courseId}01`, // Mock Code
                    semester: "Fall 2024", // Mock Semester String
                    studentCount: 50 + Number(courseId || 0), // Mock Count
                    documentCount: 5 + Number(courseId || 0), // Mock Count (will be replaced by actual count below)
                };
                setCourse(mockData);
                // --- END MOCK DATA ---

            } catch (err: any) {
                setCourseError(err.message || "Failed to load course details.");
            } finally {
                setIsLoadingCourse(false);
            }
        };
        fetchCourseDetails();
    }, [courseId]);
    // --- End Fetch Course Details ---


    // --- Fetch Course Documents ---
    useEffect(() => {
        if (!courseId) {
            setDocsError("Course ID needed to fetch documents.");
            setIsLoadingDocs(false);
            return;
        }
        const fetchDocuments = async () => {
            setIsLoadingDocs(true);
            setDocsError(null);
            const url = `http://localhost:8000/courses/${courseId}/documents`;
            console.log(`Fetching documents from: ${url}`);
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Failed to fetch documents (Status: ${response.status})`);
                }
                const data: Document[] = await response.json();
                // Map API data to UI structure
                setDocuments(data.map(doc => ({
                    ...doc,
                    name: doc.file_name, // Map field name
                    uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
                    type: doc.file_name.split('.').pop()?.toUpperCase() || 'FILE',
                    size: 'N/A' // Size not provided by list endpoint
                })));
            } catch (err: any) {
                console.error("Fetch documents error:", err);
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setDocsError("Could not connect to server to get documents.");
                } else {
                    setDocsError(err.message || "Failed to load documents.");
                }
                // Also set mock data on error if needed for testing UI
                // const mockDocs: Document[] = [
                //     { id: 'doc1', name: 'Lecture 1.pdf', type: 'PDF', size: '2.5 MB', uploadDate: '2024-01-15', courseId: courseId },
                // ];
                // setDocuments(mockDocs);
            } finally {
                setIsLoadingDocs(false);
            }
        };
        fetchDocuments();
    }, [courseId]);
    // --- End Fetch Course Documents ---


    // --- Handlers ---
    const handleFilesSelected = (files: File[]) => {
        console.log('Files selected for upload:', files);
        // TODO: Implement file upload logic to POST /courses/{courseId}/documents
        alert(`Simulating upload for ${files.length} file(s). Check console.`);
        setIsAddDocumentOpen(false);
        // Consider re-fetching documents list after successful upload
    };
    // --- End Handlers ---


    // --- Loading/Error/Not Found States ---
    if (isLoadingCourse) {
        return <div className="text-center p-10">Loading course details...</div>;
    }
    if (courseError) {
        return <div className="text-center text-destructive p-10">Error loading course: {courseError}</div>;
    }
    if (!course) {
        return <div className="text-center p-10">Course not found.</div>;
    }
    // --- End States ---


    // --- Main Render ---
    return (
        // Removed outer container/mx-auto
        <div className="space-y-6">
            {/* Course header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="text-center sm:text-left">
                    {/* Back button (optional, depends on navigation flow) */}
                    {/* <Button variant="ghost" onClick={() => navigate(-1)} className="mb-2 hidden sm:inline-flex">← Back</Button> */}
                    <h1 className="text-2xl sm:text-3xl font-bold break-words">
                        {course.name}
                    </h1>
                    <p className="text-muted-foreground text-sm sm:text-base">
                        {/* Display code if available, otherwise semester/year */}
                        {course.code ? `${course.code} • ` : ''}
                        {course.semester || semesterIdToString(course.semester_id)} {course.year}
                    </p>
                </div>
                <div className="flex justify-center sm:justify-end">
                    <Button className="w-full sm:w-auto" onClick={() => setIsAddDocumentOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Document
                    </Button>
                </div>
            </div>

            {/* Course Stats - RATING REMOVED */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4"> {/* Changed to sm:grid-cols-2 */}
                <Card className="text-center">
                    <CardContent className="p-4">
                        {/* Use placeholder or fetched data */}
                        <div className="text-2xl font-bold">{course.studentCount ?? 'N/A'}</div>
                        <div className="text-sm text-muted-foreground">Students Enrolled</div>
                    </CardContent>
                </Card>
                <Card className="text-center">
                    <CardContent className="p-4">
                        {/* Use actual length of fetched documents array */}
                        <div className="text-2xl font-bold">{isLoadingDocs ? '...' : documents.length}</div>
                        <div className="text-sm text-muted-foreground">Documents</div>
                    </CardContent>
                </Card>
                {/* Rating card completely removed */}
            </div>

            {/* Course Documents */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg sm:text-xl text-center sm:text-left">
                        Course Documents
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {/* Documents Loading State */}
                    {isLoadingDocs && <p className="text-sm text-muted-foreground text-center py-4">Loading documents...</p>}
                    {/* Documents Error State */}
                    {docsError && !isLoadingDocs && <p className="text-sm text-destructive text-center py-4">Error: {docsError}</p>}
                    {/* Documents List */}
                    {!isLoadingDocs && !docsError && (
                        <div className="space-y-3">
                            {documents.map((doc) => (
                                <div
                                    key={doc.id}
                                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors" // Added hover effect
                                >
                                    {/* Doc Info */}
                                    <div className="flex items-center gap-3 overflow-hidden">
                                        <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                                            <span className="text-xs font-medium uppercase">{doc.type || 'FILE'}</span>
                                        </div>
                                        <div className="min-w-0"> {/* Helps with truncation */}
                                            {/* --- NO ERROR HERE ANYMORE --- */}
                                            <p className="font-medium text-sm sm:text-base truncate" title={doc.name}>
                                                {doc.name || doc.file_name}
                                            </p>
                                            {/* --- NO ERROR HERE ANYMORE --- */}
                                            <p className="text-xs sm:text-sm text-muted-foreground">
                                                {doc.size ? `${doc.size} • ` : ''}
                                                Uploaded: {doc.uploadDate || new Date(doc.uploaded_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                    {/* Doc Actions */}
                                    <div className="flex justify-end sm:justify-start gap-1 sm:gap-2 flex-shrink-0">
                                        {/* TODO: Implement action handlers */}
                                        <Button variant="ghost" size="sm" title="View Document (Not Implemented)">
                                            <Eye className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm" title="Download Document (Not Implemented)">
                                            <Download className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm" title="Delete Document (Not Implemented)" className="text-destructive hover:text-destructive">
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                            {/* No Documents Message */}
                            {documents.length === 0 && (
                                <p className="text-sm text-muted-foreground text-center py-4">
                                    No documents uploaded for this course yet.
                                </p>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Add Document Dialog */}
            <Dialog open={isAddDocumentOpen} onOpenChange={setIsAddDocumentOpen}>
                <DialogContent className="max-w-md sm:max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Upload Documents for {course?.name || 'this course'}</DialogTitle>
                    </DialogHeader>
                    <div className="py-4"> {/* Added padding */}
                        <FileUpload onFilesSelected={handleFilesSelected} />
                    </div>
                    <div className="flex flex-col sm:flex-row justify-end gap-2"> {/* Footer area */}
                        <Button
                            variant="outline"
                            onClick={() => setIsAddDocumentOpen(false)}
                            className="w-full sm:w-auto"
                        >
                            Cancel
                        </Button>
                        {/* Upload action is triggered by onFilesSelected in this setup */}
                        {/* <Button className="w-full sm:w-auto">Upload</Button> */}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}

