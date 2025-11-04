import { useParams, useNavigate, useLocation } from "react-router-dom";
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
// --- 1. IMPORT THE API CLIENT HOOK ---
import { useApiClient } from "../ApiClientContext";

// --- Define Interfaces ---
interface CourseDetail {
    id: string;
    instructor_id: string;
    name: string;
    institution: string;
    semester_id: number;
    year: number;
    created_at: string;
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

function semesterIdToNumber(semester: string | undefined): number {
    if (semester === "Spring") return 1;
    if (semester === "Summer") return 2;
    if (semester === "Fall") return 4;
    return 4;
}
// --- End Helper Functions ---


export function CoursePage() {
    const { courseId } = useParams<{ courseId: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    // --- 2. INITIALIZE API CLIENT ---
    const apiClient = useApiClient();

    // --- State (from your version) ---
    const navigatedState = location.state as { courseName?: string, courseCode?: string, institution?: string, semester?: string, year?: number };
    const initialCourseName = navigatedState?.courseName || `Course ${courseId} Details`;
    const initialCourseCode = navigatedState?.courseCode || `CS ${courseId}01`;
    const initialInstitution = navigatedState?.institution || "Mock University";
    const initialSemesterId = navigatedState?.semester ? semesterIdToNumber(navigatedState.semester) : 4;
    const initialYear = navigatedState?.year || new Date().getFullYear();

    const [course, setCourse] = useState<CourseDetail | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isLoadingCourse, setIsLoadingCourse] = useState(true);
    const [isLoadingDocs, setIsLoadingDocs] = useState(true);
    const [courseError, setCourseError] = useState<string | null>(null);
    const [docsError, setDocsError] = useState<string | null>(null);
    const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);
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
                console.warn(`Using MOCK DATA for course details: ${courseId}`);
                await new Promise(res => setTimeout(res, 500));
                const mockData: CourseDetail = {
                    id: courseId,
                    instructor_id: "76dcf3ac-b500-4787-8ef7-f2ed2843f1f7", // !! PLACEHOLDER UUID !!
                    name: initialCourseName,
                    institution: initialInstitution,
                    semester_id: initialSemesterId,
                    year: initialYear,
                    created_at: new Date().toISOString(),
                    code: initialCourseCode,
                    semester: semesterIdToString(initialSemesterId),

                    // --- 3. FIX FOR 'NaN' WARNING ---
                    studentCount: 50, // Use a static mock number
                    documentCount: 5, // Use a static mock number
                    // --- END FIX ---
                };
                setCourse(mockData);
            } catch (err: any) {
                console.error("Fetch course details error:", err);
                setCourseError(err.message || "Failed to load course details.");
            } finally {
                setIsLoadingCourse(false);
            }
        };
        fetchCourseDetails();
    }, [courseId, initialCourseName, initialCourseCode, initialInstitution, initialSemesterId, initialYear]);
    // --- End Fetch Course Details ---


    // --- 4. FETCH COURSE DOCUMENTS (USING API CLIENT) ---
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
                // --- REPLACED 'fetch' WITH 'apiClient.listDocuments' ---
                // This will now send your login token!
                const { data, errorMessage } = await apiClient.listDocuments(courseId, {
                    order_by: "uploaded_at",
                    order_dir: "desc"
                });

                if (errorMessage) {
                    // This will now correctly throw the "Not authenticated" error
                    throw new Error(errorMessage);
                }

                // APIClient returns { total: number, documents: [] }
                const mappedData = (data.documents || []).map((doc: any) => ({
                    ...doc,
                    name: doc.file_name,
                    uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
                    type: doc.file_name.split('.').pop()?.toUpperCase() || 'FILE',
                    size: 'N/A' // Size not provided by list endpoint
                }));
                setDocuments(mappedData);

            } catch (err: any) {
                console.error("Fetch documents error:", err);
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setDocsError("Could not connect to server to get documents.");
                } else {
                    // This will now show "Not authenticated" or "401"
                    setDocsError(err.message || "Failed to load documents.");
                }
            } finally {
                setIsLoadingDocs(false);
            }
        };
        fetchDocuments();
    }, [courseId, apiClient]); // Added apiClient as dependency
    // --- End Fetch Course Documents ---


    // --- 5. HANDLERS (UPDATED TO USE API CLIENT) ---
    const handleFilesSelected = async (files: File[]) => {
        if (!courseId) return;
        console.log('Files selected for upload:', files);

        // --- REAL UPLOAD LOGIC ---
        setIsLoadingDocs(true); // Re-use doc loading state
        let hadError = false;
        try {
            for (const file of files) {
                // Use the apiClient to upload
                const { errorMessage } = await apiClient.uploadDocument(courseId, file);
                if (errorMessage) {
                    console.error(`Failed to upload ${file.name}:`, errorMessage);
                    hadError = true;
                }
            }
        } catch (err: any) {
            console.error("Upload error:", err);
            setDocsError(err.message || "An error occurred during upload.");
            hadError = true;
        } finally {
            setIsAddDocumentOpen(false);
            // Always refresh the document list
            console.log("Upload finished, refreshing documents...");

            // Re-fetch documents
            const url = `http://localhost:8000/courses/${courseId}/documents`;
            const response = await fetch(url);
            const data: Document[] = await response.json();
            setDocuments(data.map(doc => ({
                ...doc,
                name: doc.file_name,
                uploadDate: new Date(doc.uploaded_at).toLocaleDateString(),
                type: doc.file_name.split('.').pop()?.toUpperCase() || 'FILE',
                size: 'N/A'
            })));
            setIsLoadingDocs(false);

            if (hadError) {
                setDocsError("One or more files failed to upload.");
            }
        }
    };

    const handleDeleteCourse = async () => {
        if (!courseId || !course?.instructor_id) {
            setDeleteError("Cannot delete: Course ID or Instructor ID is missing.");
            return;
        }

        setIsDeleting(true);
        setDeleteError(null);

        try {
            // --- USE API CLIENT TO DELETE ---
            const { errorMessage } = await apiClient.request(
                "DELETE",
                `/courses/${courseId}`
            );

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            console.log(`Course ${courseId} deleted successfully.`);
            setIsFinalDeleteDialogOpen(false);
            setIsDeleteDialogOpen(false);
            setIsSettingsOpen(false);
            navigate(`/instructors/${course.instructor_id}/courses`);

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
                    <Button
                        variant="ghost"
                        onClick={() => navigate(`/instructors/${course.instructor_id}/courses`)}
                        className="mb-2 -ml-4"
                    >
                        ← Back to Courses
                    </Button>
                    <h1 className="text-2xl sm:text-3xl font-bold break-words">
                        {course.name}
                    </h1>
                    <p className="text-muted-foreground text-sm sm:text-base">
                        {course.code ? `${course.code} • ` : ''}
                        {course.semester || semesterIdToString(course.semester_id)} {course.year}
                    </p>
                </div>

                {/* Button Group */}
                <div className="flex justify-center sm:justify-end gap-2">
                    <Button className="w-full sm:w-auto" onClick={() => setIsAddDocumentOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Document
                    </Button>

                    {/* Settings Popover */}
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
                                {/* Delete Option (Triggers First Dialog) */}
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
                                            {/* Second Confirmation Dialog (Nested Trigger) */}
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

