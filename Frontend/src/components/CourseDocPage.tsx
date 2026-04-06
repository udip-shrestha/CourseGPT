import { useState, useEffect, useCallback } from "react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Plus, ChevronLeft, ChevronRight } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { FileUpload } from "./FileUpload";
import { useApiClient } from "../clients/ApiClientContext.tsx";
import { DocumentActions } from "./DocumentAction.tsx";






export function CourseDocPage({ course }: { course: any }) {
    const { documentClient } = useApiClient();

    const { courseClient } = useApiClient();

    const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);
    const [isAddCanvasOpen, setIsAddCanvasOpen] = useState(false);
    const [canvasFiles, setCanvasFiles] = useState<any[]>([]);
    const [selectedCanvasIds, setSelectedCanvasIds] = useState<Set<number>>(new Set());
    const [isCanvasLinked, setIsCanvasLinked] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [docToDelete, setDocToDelete] = useState<string | null>(null);
    const [documents, setDocuments] = useState<any[]>([]);
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState("");

    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const limit = 5;

    const fetchDocuments = useCallback(async () => {
        if (!course?.id) return;

        setError(null);
        setLoading(true);
        const offset = (page - 1) * limit;

        const { data, errorMessage } = await documentClient.listDocuments(course.id, {
            file_name: searchTerm,
            order_by: "uploaded_at",
            order_dir: "desc",
            limit,
            offset,
        });

        if (errorMessage) {
            setDocuments([]);
            setTotal(0);
            setError(errorMessage);
        } else if (data) {
            setDocuments(data.documents || []);
            setTotal(data.total || 0);
        }

        setLoading(false);
    }, [course?.id, page, searchTerm]);

    const checkCanvasLinked = useCallback(async () => {
        if (!course?.id) return;
        const { data, errorMessage } = await courseClient.isCanvasLinked(course.id);
        if (errorMessage) {
            setIsCanvasLinked(false);
        } else if (data) {
            setIsCanvasLinked(Boolean(data.linked));
        }
    }, [course?.id]);

    const loadCanvasFiles = useCallback(async () => {
        if (!course?.id) return;
        setError(null);
        setLoading(true);
        const { data, errorMessage } = await courseClient.getCanvasFiles(course.id);
        if (errorMessage) {
            setError(errorMessage);
            setCanvasFiles([]);
        } else if (data) {
            setCanvasFiles(data || []);
        }
        setLoading(false);
    }, [course?.id]);

    useEffect(() => {
        const delay = setTimeout(() => {
            fetchDocuments();
        }, 500);
        return () => clearTimeout(delay);
    }, [searchTerm, fetchDocuments]);    

    useEffect(() => {
        checkCanvasLinked();
    }, [checkCanvasLinked]);

    async function handleUpload() {
        if (selectedFiles.length === 0) {
            setUploadError("Please select a file to upload.");
            return;
        }

        setUploadError(null);
        setLoading(true);
        try {
            for (const file of selectedFiles) {
                const { errorMessage } = await documentClient.uploadDocument(course.id, file);
                if (errorMessage) {
                    setUploadError(`Failed to upload ${file.name}: ${errorMessage}`);
                    setLoading(false);
                    return; // keep dialog open
                }
            }

            setPage(1);
            await fetchDocuments();
            setIsAddDocumentOpen(false);
        } catch {
            setUploadError("Unexpected error while uploading. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    async function handleConfirmDelete() {
        if (!docToDelete) return;
        setLoading(true);
        setDeleteError(null);

        const { errorMessage } = await documentClient.deleteDocument(course.id, docToDelete);
        if (errorMessage) {
            setDeleteError("Failed to delete document. Please try again.");
        } else {
            await fetchDocuments();
            setIsDeleteDialogOpen(false);
        }

        setLoading(false);
        setDocToDelete(null);
    }

    function openDeleteDialog(docId: string) {
        setDocToDelete(docId);
        setIsDeleteDialogOpen(true);
    }

    async function handleDownload(docId: string, fallbackName: string) {
        const { data, errorMessage } = await documentClient.downloadDocument(course.id, docId);
    
        if (errorMessage || !data?.blob) {
            setError(errorMessage || "Failed to download document.");
            return;
        }
    
        const link = document.createElement("a");
        link.href = URL.createObjectURL(data.blob);
        link.download = data.fileName || fallbackName || "download";
        
        link.click();
        URL.revokeObjectURL(link.href);
    }

    async function handlePreview(docId: string) {
        const { data, errorMessage } = await documentClient.previewDocument(course.id, docId);
    
        if (errorMessage || !data?.blob) {
            setError(errorMessage || "Failed to preview document.");
            return;
        }
    
        const url = URL.createObjectURL(data.blob);
        window.open(url, "_blank");
    }
    
    const totalPages = Math.max(1, Math.ceil(total / limit));
    const canPrev = page > 1;
    const canNext = page < totalPages;

    return (
        <>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
                <h2 className="text-xl font-semibold">Course Documents</h2>
                <div className="flex gap-2">
                    <Button
                        className="mt-3 sm:mt-0 w-full sm:w-auto"
                        onClick={() => setIsAddDocumentOpen(true)}
                        disabled={loading}
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        Add Document
                    </Button>

                    {isCanvasLinked && (
                        <Button
                            className="mt-3 sm:mt-0 w-full sm:w-auto"
                            onClick={async () => {
                                setIsAddCanvasOpen(true);
                                await loadCanvasFiles();
                            }}
                            disabled={loading}
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            Add Canvas files
                        </Button>
                    )}
                </div>
            </div>

            {/* Search Bar */}
            <div className="flex gap-4 mb-5">
                <div className="relative flex-1">
                    <svg
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        viewBox="0 0 24 24"
                    >
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>

                    <input
                        placeholder="Search documents by name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 w-full border rounded-md px-3 py-2 text-sm"
                    />
                </div>
            </div>

            <Card>
                <CardContent>
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <p className="text-muted-foreground">Loading documents...</p>
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                            <p className="text-destructive font-medium mb-2">
                                Failed to load course documents.
                            </p>
                            <p className="text-sm text-muted-foreground mb-4">{error}</p>
                            <Button variant="outline" onClick={fetchDocuments} disabled={loading}>
                                Retry
                            </Button>
                        </div>
                    ) : documents.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-3">
                                <Plus className="h-6 w-6 text-muted-foreground" />
                            </div>
                            <p className="font-medium text-gray-800 dark:text-gray-200">
                                No documents uploaded yet
                            </p>
                            <p className="text-sm text-muted-foreground mt-1 mb-4 max-w-sm">
                                Upload PDFs or notes to make them available for CourseGPT to reference.
                            </p>
                        </div>
                    ) : (
                        <>
                            <div className="space-y-3 py-7">
                                {documents.map((doc) => (
                                    <div
                                        key={doc.id}
                                        className="flex items-center justify-between p-4 border rounded-lg"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                                            <span className="text-xs font-medium">
                                                {(() => {
                                                    if (!doc.file_name) return "TEXT";

                                                    const parts = doc.file_name.split(".");
                                                    if (parts.length < 2) return "TEXT";

                                                    const ext = parts.pop()?.trim();
                                                    return ext ? ext.toUpperCase() : "TEXT";
                                                })()}
                                            </span>
                                            </div>
                                            <div>
                                                <p className="font-medium">{doc.file_name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {new Date(doc.uploaded_at).toLocaleString()}
                                                </p>
                                            </div>
                                        </div>
                                        <DocumentActions
                                            courseId={course.id}
                                            doc={doc}
                                            onPreview={() => handlePreview(doc.id)}
                                            onDownload={() => handleDownload(doc.id, doc.file_name)}
                                            onDelete={() => openDeleteDialog(doc.id)}
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="flex items-center justify-center gap-4 mt-6">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage((p) => p - 1)}
                                    disabled={!canPrev || loading}
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </Button>

                                <span className="text-sm text-muted-foreground">
                                    Page {page} of {totalPages}
                                </span>

                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage((p) => p + 1)}
                                    disabled={!canNext || loading}
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </Button>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>

            {/* Upload Dialog */}
            <Dialog open={isAddDocumentOpen} onOpenChange={setIsAddDocumentOpen}>
                <DialogContent className="max-w-md sm:max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Upload Documents for {course.name}</DialogTitle>
                    </DialogHeader>

                    <FileUpload
                        onFilesSelected={(files) => {
                            setSelectedFiles(files);
                            setUploadError(null);
                        }}
                    />

                    {uploadError && (
                        <p className="text-sm text-destructive mt-2 bg-destructive/10 border border-destructive/30 rounded-md p-2">
                            {uploadError}
                        </p>
                    )}

                    <div className="flex justify-end gap-2 mt-4">
                        <Button variant="outline" onClick={() => setIsAddDocumentOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleUpload} disabled={loading}>
                            {loading ? "Uploading..." : "Upload"}
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Canvas Files Dialog */}
            <Dialog open={isAddCanvasOpen} onOpenChange={setIsAddCanvasOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>Import Canvas files for {course.name}</DialogTitle>
                    </DialogHeader>

                    <div className="py-3">
                        {loading ? (
                            <p className="text-muted-foreground">Loading canvas files...</p>
                        ) : canvasFiles.length === 0 ? (
                            <p className="text-sm text-muted-foreground">No files found in Canvas for this course.</p>
                        ) : (
                            <div className="space-y-2 max-h-72 overflow-y-auto">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-medium">Select files to import</label>
                                    <button
                                        className="text-sm text-primary hover:underline"
                                        onClick={() => {
                                            // toggle select all
                                            const allIds = new Set(canvasFiles.map((f: any) => f.id));
                                            const currentlySelected = selectedCanvasIds;
                                            if (currentlySelected.size === canvasFiles.length) {
                                                setSelectedCanvasIds(new Set());
                                            } else {
                                                setSelectedCanvasIds(allIds);
                                            }
                                        }}
                                    >
                                        Toggle All
                                    </button>
                                </div>

                                {canvasFiles.map((f: any) => (
                                    <div key={f.id} className="flex items-center justify-between p-2 rounded-md border bg-card">
                                        <div className="flex items-center gap-3">
                                            <input
                                                type="checkbox"
                                                checked={selectedCanvasIds.has(f.id)}
                                                onChange={() => {
                                                    const newSet = new Set(selectedCanvasIds);
                                                    if (newSet.has(f.id)) newSet.delete(f.id);
                                                    else newSet.add(f.id);
                                                    setSelectedCanvasIds(newSet);
                                                }}
                                            />
                                            <div>
                                                <p className="font-medium text-gray-800 dark:text-gray-200">{f.display_name || f.filename}</p>
                                                <p className="text-xs text-muted-foreground">{f.size ? `${Math.round(f.size/1024)} KB` : ''}</p>
                                            </div>
                                        </div>
                                        <a className="text-sm text-muted-foreground hover:underline" href={f.url} target="_blank" rel="noreferrer">Open</a>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="flex justify-end gap-2 mt-4">
                        <Button variant="outline" onClick={() => setIsAddCanvasOpen(false)}>Cancel</Button>
                        <Button
                            onClick={async () => {
                                if (selectedCanvasIds.size === 0) {
                                    setUploadError("Please select at least one canvas file to import.");
                                    return;
                                }

                                setUploadError(null);
                                setLoading(true);
                                try {
                                    // For each selected, fetch the file blob and upload
                                    for (const f of canvasFiles.filter((cf) => selectedCanvasIds.has(cf.id))) {
                                        try {
                                            const resp = await fetch(f.url);
                                            const blob = await resp.blob();
                                            const fileName = f.display_name || decodeURIComponent(f.filename || 'file');
                                            const file = new File([blob], fileName, { type: blob.type || 'application/octet-stream' });
                                            const { errorMessage } = await documentClient.uploadDocument(course.id, file);
                                            if (errorMessage) {
                                                setUploadError(`Failed to import ${fileName}: ${errorMessage}`);
                                                break;
                                            }
                                        } catch (e) {
                                            setUploadError(`Failed to fetch/import file ${f.display_name || f.filename}`);
                                            break;
                                        }
                                    }

                                    await fetchDocuments();
                                    setIsAddCanvasOpen(false);
                                    setSelectedCanvasIds(new Set());
                                } finally {
                                    setLoading(false);
                                }
                            }}
                            disabled={loading}
                        >
                            {loading ? "Importing..." : "Import Selected"}
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Delete Dialog */}
            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent className="max-w-sm">
                    <DialogHeader>
                        <DialogTitle className="text-destructive">Delete Document</DialogTitle>
                    </DialogHeader>
                    {deleteError && (
                        <p className="text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-md p-2 mb-2">
                            {deleteError}
                        </p>
                    )}
                    <p className="text-sm text-muted-foreground">
                        Are you sure you want to permanently delete this document? This action{" "}
                        <strong>cannot be undone</strong>.
                    </p>
                    <div className="flex justify-end gap-2 mt-4">
                        <Button
                            variant="outline"
                            onClick={() => {
                                setDocToDelete(null);
                                setIsDeleteDialogOpen(false);
                            }}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleConfirmDelete}
                            disabled={loading}
                        >
                            {loading ? "Deleting..." : "Delete"}
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
}
