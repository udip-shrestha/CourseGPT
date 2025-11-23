import { useState, useEffect, useCallback } from "react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Plus, Download, Trash2, Eye, ChevronLeft, ChevronRight } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { FileUpload } from "./FileUpload";
import { useApiClient } from "../clients/ApiClientContext.tsx";






export function CourseDocPage({ course }: { course: any }) {
    const { documentClient } = useApiClient();

    const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [docToDelete, setDocToDelete] = useState<string | null>(null);
    const [documents, setDocuments] = useState<any[]>([]);
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null);

    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const limit = 5;

    const fetchDocuments = useCallback(async () => {
        if (!course?.id) return;

        setError(null);
        setLoading(true);
        const offset = (page - 1) * limit;

        const { data, errorMessage } = await documentClient.listDocuments(course.id, {
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
    }, [course?.id, page]);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

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
                <Button
                    className="mt-3 sm:mt-0 w-full sm:w-auto"
                    onClick={() => setIsAddDocumentOpen(true)}
                    disabled={loading}
                >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Document
                </Button>
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
                                        <div className="flex gap-2">
                                            {/* Preview Button */}
                                            {doc.can_preview && (
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handlePreview(doc.id)}
                                                >
                                                    <Eye className="h-4 w-4" />
                                                </Button>
                                            )}

                                            {/* Download Button */}
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDownload(doc.id, doc.file_name)}
                                            >
                                                <Download className="h-4 w-4" />
                                            </Button>

                                            {/* Delete Button */}
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => openDeleteDialog(doc.id)}
                                            >
                                                <Trash2 className="h-4 w-4 text-destructive" />
                                            </Button>
                                        </div>

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
