import { useParams, useNavigate, useLocation } from "react-router-dom"; // 1. Added useLocation and useNavigate
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Plus, Eye, Download, Trash2, Settings, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogClose,
    DialogFooter,
    DialogTrigger
} from "./ui/dialog";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { FileUpload } from "./FileUpload";

// --- Define Interfaces ---
interface CourseDetail {
    id: string;
    instructor_id: string; // Now required
    name: string;
    institution: string; // Now required
    semester_id: number; // Now required
    year: number;       // Now required
    created_at: string; // Now required
    code?: string;
    semester?: string;
    studentCount?: number;
    documentCount?: number;
}

interface Document {
    id: string;
    file_name: string;
    uploaded_at: string;
    name: string;
    uploadDate: string;
    type?: string;
    size?: string;
}
// --- End Interfaces ---

// --- Helper Functions ---
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

// --- ADDED HELPER ---
// Converts string name back to ID. Adjust mapping to be the reverse of semesterIdToString
function semesterIdToNumber(semester: string | undefined): number {
    if (semester === "Spring") return 1;
    if (semester === "Summer") return 2;
    if (semester === "Fall") return 4; // Based on Swagger/CourseCard
    return 4; // Default to Fall
}
// --- END HELPER ---


export function CoursePage() {
    const { courseId } = useParams<{ courseId: string }>();
    const navigate = useNavigate(); // 2. Re-added navigate
    const location = useLocation(); // 3. Get location to read state

    // 4. Try to get course name/code from navigation state
    const navigatedState = location.state as { courseName?: string, courseCode?: string, institution?: string, semester?: string, year?: number };
    const initialCourseName = navigatedState?.courseName || `Course ${courseId} Details`; // Fallback
    const initialCourseCode = navigatedState?.courseCode || `CS ${courseId}01`; // Fallback
    const initialInstitution = navigatedState?.institution || "Mock University";
    const initialSemesterId = navigatedState?.semester ? semesterIdToNumber(navigatedState.semester) : 4; // Use helper
    const initialYear = navigatedState?.year || new Date().getFullYear(); // Default to current year
    // --- (End of changes) ---

    // --- State ---
    const [course, setCourse] = useState<CourseDetail | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isLoadingCourse, setIsLoadingCourse] = useState(true);
    const [isLoadingDocs, setIsLoadingDocs] = useState(true);
    const [courseError, setCourseError] = useState<string | null>(null);
    const [docsError, setDocsError] = useState<string | null>(null);
    const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);

    // --- State for Popover and Dialogs ---
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isFinalDeleteDialogOpen, setIsFinalDeleteDialogOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState<string | null>(null);
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
                // --- REVERTED TO MOCK DATA ---
                console.warn(`Using MOCK DATA for course details: ${courseId}`);

                // --- COMMENTED OUT FAILING FETCH ---
                // const response = await fetch(`http://localhost:8000/courses/${courseId}`);
                // if (!response.ok) { ... }
                // const data: CourseDetail = await response.json();

                // --- MOCK DATA BLOCK (Updated) ---
                await new Promise(res => setTimeout(res, 500)); // Simulate fetch time
                const mockData: CourseDetail = {
                    id: courseId,
                    // !!! IMPORTANT: Using a placeholder UUID for navigation.
                    // This MUST be provided by your GET /courses/{id} endpoint eventually.
                    instructor_id: "76dcf3ac-b500-4787-8ef7-f2ed2843f1f7", // !! PLACEHOLDER UUID !!

                    // --- 5. Use name/code from navigation state ---
                    name: initialCourseName,
                    institution: initialInstitution,
                    semester_id: initialSemesterId,
                    year: initialYear,
                    created_at: new Date().toISOString(),
                    code: initialCourseCode,
                    semester: semesterIdToString(initialSemesterId),
                    // --- (End of changes) ---

                    studentCount: 50 + Number(courseId || 0), // Mock Count
                    documentCount: 5 + Number(courseId || 0), // Mock Count (will be replaced by actual count below)
                };
                setCourse(mockData);
                // --- END MOCK DATA ---

            } catch (err: any) {
                console.error("Fetch course details error:", err);
                setCourseError(err.message || "Failed to load course details.");
            } finally {
                setIsLoadingCourse(false);
            }
        };
        fetchCourseDetails();
    }, [courseId, initialCourseName, initialCourseCode, initialInstitution, initialSemesterId, initialYear]); // 6. Added new dependencies
    // --- End Fetch Course Details ---


    // --- Fetch Course Documents ---
    useEffect(() => {
        if (!courseId) {
            setDocsError("Course ID needed to fetch documents.");
            setIsLoadingDocs(false);
            return;
        }
        // This endpoint IS working according to your logs (200 OK)
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
                setDocuments(data.map(doc => ({
                    ...doc,
                    name: doc.file_name,
                    uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
                    type: doc.file_name.split('.').pop()?.toUpperCase() || 'FILE',
                    size: 'N/A'
                })));
            } catch (err: any) {
                console.error("Fetch documents error:", err);
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setDocsError("Could not connect to server to get documents.");
                } else {
                    setDocsError(err.message || "Failed to load documents.");
                }
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
        alert(`Simulating upload for ${files.length} file(s). Check console.`);
        setIsAddDocumentOpen(false);
    };

    // --- Delete Course Handler ---
    const handleDeleteCourse = async () => {
        if (!courseId || !course?.instructor_id) { // Check for instructor_id from course state
            setDeleteError("Cannot delete: Course ID or Instructor ID is missing.");
            return;
        }

        setIsDeleting(true);
        setDeleteError(null);

        try {
            // This endpoint IS working according to your Swagger
            const response = await fetch(`http://localhost:8000/courses/${courseId}`, {
                method: 'DELETE',
                headers: { 'accept': '*/*' }
            });

            if (response.status === 204 || response.ok) {
                console.log(`Course ${courseId} deleted successfully.`);
                setIsFinalDeleteDialogOpen(false);
                setIsDeleteDialogOpen(false);
                setIsSettingsOpen(false);
                // Use the instructor_id from the course state to navigate back
                navigate(`/instructors/${course.instructor_id}/courses`);
            } else {
                let errorDetail = `Failed to delete course (Status: ${response.status})`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                } catch (_) {}
                throw new Error(errorDetail);
            }
        } catch (err: any) {
            console.error("Failed to delete course:", err);
            let userError = err.message || "An unexpected error occurred.";
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                userError = "Could not connect to the server.";
            }
            setDeleteError(userError);
        } finally {
            setIsDeleting(false);
        }
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

    return (
        <div className="space-y-6">
            {/* Course header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="text-center sm:text-left">
                    {/* --- Back Button (uses mock instructor_id for now) --- */}
                    <Button
                        variant="ghost"
                        onClick={() => navigate(`/instructors/${course.instructor_id}/courses`)} // 7. Added Back Button logic
                        className="mb-2 -ml-4"
                    >
                        ← Back to Courses
                    </Button>
                    {/* --------------------- */}
                    <h1 className="text-2xl sm:text-3xl font-bold break-words">
                        {course.name}
                    </h1>
                    <p className="text-muted-foreground text-sm sm:text-base">
                        {course.code ? `${course.code} • ` : ''}
                        {course.semester || semesterIdToString(course.semester_id)} {course.year}
                    </p>
                </div>

                {/* --- Button Group --- */}
                <div className="flex justify-center sm:justify-end gap-2">
                    <Button className="w-full sm:w-auto" onClick={() => setIsAddDocumentOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Document
                    </Button>

                    {/* --- Settings Popover --- */}
                    <Popover open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                        <PopoverTrigger asChild>
                            <Button variant="outline" size="icon" aria-label="Course Settings">
                                <Settings className="h-5 w-5" />
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-48 p-2">
                            <div className="grid gap-1">
                                <Button
                                    variant="ghost"
                                    className="w-full justify-start text-sm h-8"
                                    disabled // Update endpoint not implemented
                                    onClick={() => {
                                        console.log("Update course clicked");
                                        setIsSettingsOpen(false);
                                    }}
                                >
                                    Update Course
                                </Button>
                                {/* --- Delete Option (Triggers First Dialog) --- */}
                                <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                                    <DialogTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10 text-sm h-8"
                                            onClick={() => setIsSettingsOpen(false)} // Close popover
                                        >
                                            <Trash2 className="mr-2 h-4 w-4" />
                                            Delete Course
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent>
                                        <DialogHeader>
                                            <DialogTitle>Delete "{course.name}"?</DialogTitle>
                                            <DialogDescription>
                                                This action cannot be undone immediately. Do you want to proceed?
                                            </DialogDescription>
                                        </DialogHeader>
                                        <DialogFooter className="gap-2 sm:justify-end">
                                            <DialogClose asChild>
                                                <Button variant="outline">Cancel</Button>
                                            </DialogClose>
                                            {/* --- Second Confirmation Dialog (Nested Trigger) --- */}
                                            <Dialog open={isFinalDeleteDialogOpen} onOpenChange={setIsFinalDeleteDialogOpen}>
                                                <DialogTrigger asChild>
                                                    <Button variant="destructive">Confirm Delete</Button>
                                                </DialogTrigger>
                                                <DialogContent>
                                                    <DialogHeader>
                                                        <DialogTitle className="flex items-center gap-2">
                                                            <AlertTriangle className="text-destructive h-5 w-5"/> Final Confirmation
                                                        </DialogTitle>
                                                        <DialogDescription>
                                                            Deleting this course is permanent and will remove all associated documents.
                                                            {deleteError && <p className="text-sm text-destructive mt-4">Error: {deleteError}</p>}
                                                        </DialogDescription>
                                                    </DialogHeader>
                                                    <DialogFooter className="gap-2">
                                                        <Button
                                                            variant="outline"
                                                            onClick={() => setIsFinalDeleteDialogOpen(false)}
                                                            disabled={isDeleting}
                                                        >
                                                            Cancel
                                                        </Button>
                                                        <Button
                                                            variant="destructive"
                                                            onClick={handleDeleteCourse} // Calls API
                                                            disabled={isDeleting}
                                                        >
                                                            {isDeleting ? "Deleting..." : "Yes, Delete Permanently"}
                                                        </Button>
                                                    </DialogFooter>
                                                </DialogContent>
                                            </Dialog>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            </div>
                        </PopoverContent>
                    </Popover>
                    {/* --- End Settings --- */}
                </div>
                {/* --- END UPDATED Button Group --- */}
            </div>

            {/* Course Stats - RATING REMOVED */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <Card className="text-center">
                    <CardContent className="p-4">
                        <div className="text-2xl font-bold">{course.studentCount ?? 'N/A'}</div>
                        <div className="text-sm text-muted-foreground">Students Enrolled</div>
                    </CardContent>
                </Card>
                <Card className="text-center">
                    <CardContent className="p-4">
                        <div className="text-2xl font-bold">{isLoadingDocs ? '...' : documents.length}</div>
                        <div className="text-sm text-muted-foreground">Documents</div>
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
                    {/* ... (Document list rendering remains the same) ... */}
                    {isLoadingDocs && <p className="text-sm text-muted-foreground text-center py-4">Loading documents...</p>}
                    {docsError && !isLoadingDocs && <p className="text-sm text-destructive text-center py-4">Error: {docsError}</p>}
                    {!isLoadingDocs && !docsError && (
                        <div className="space-y-3">
                            {documents.map((doc) => (
                                <div
                                    key={doc.id}
                                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                                >
                                    <div className="flex items-center gap-3 overflow-hidden">
                                        <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                                            <span className="text-xs font-medium uppercase">{doc.type || 'FILE'}</span>
                                        </div>
                                        <div className="min-w-0">
                                            <p className="font-medium text-sm sm:text-base truncate" title={doc.name}>
                                                {doc.name}
                                            </p>
                                            <p className="text-xs sm:text-sm text-muted-foreground">
                                                {doc.size ? `${doc.size} • ` : ''}
                                                Uploaded: {doc.uploadDate}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex justify-end sm:justify-start gap-1 sm:gap-2 flex-shrink-0">
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
                        <DialogTitle>Upload Documents for {course.name}</DialogTitle>
                    </DialogHeader>
                    <div className="py-4">
                        <FileUpload onFilesSelected={handleFilesSelected} />
                    </div>
                    <div className="flex flex-col sm:flex-row justify-end gap-2">
                        <Button
                            variant="outline"
                            onClick={() => setIsAddDocumentOpen(false)}
                            className="w-full sm:w-auto"
                        >
                            Cancel
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}

