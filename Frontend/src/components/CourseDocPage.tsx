import { useState, useEffect, useCallback } from "react";
import { Button } from "./ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Plus, Download, Trash2, ChevronLeft, ChevronRight } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { FileUpload } from "./FileUpload";
import { useApiClient } from "../ApiClientContext.tsx";
import { toast } from "sonner";

export function CourseDocPage({ course }: { course: any }) {
    const apiClient = useApiClient();

    const [isAddDocumentOpen, setIsAddDocumentOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [docToDelete, setDocToDelete] = useState<string | null>(null);
    const [documents, setDocuments] = useState<any[]>([]);
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(false);

    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const limit = 5;

    const fetchDocuments = useCallback(async () => {
        if (!course?.id) return;

        setLoading(true);
        const offset = (page - 1) * limit;

        const { data, errorMessage } = await apiClient.listDocuments(course.id, {
            order_by: "uploaded_at",
            order_dir: "desc",
            limit,
            offset,
        });

        if (errorMessage) {
            toast.error("Failed to load documents: " + errorMessage);
            setDocuments([]);
            setTotal(0);
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
            toast.warning("Please select a file to upload.");
            return;
        }

        setLoading(true);
        try {
            for (const file of selectedFiles) {
                const { errorMessage } = await apiClient.uploadDocument(course.id, file);
                if (errorMessage)
                    toast.error(`Failed to upload ${file.name}: ${errorMessage}`);
                else toast.success(`Uploaded ${file.name}`);
            }

            setPage(1);
            await fetchDocuments();
            setIsAddDocumentOpen(false);
        } catch {
            toast.error("Unexpected error while uploading.");
        } finally {
            setLoading(false);
        }
    }

    async function handleConfirmDelete() {
        if (!docToDelete) return;
        setLoading(true);

        const { errorMessage } = await apiClient.deleteDocument(course.id, docToDelete);
        console.log(errorMessage)
        if (errorMessage) toast.error("Failed to delete document.");
        else {
            toast.success("Document deleted.");
            await fetchDocuments(); // Refresh list
        }

        setLoading(false);
        setDocToDelete(null);
        setIsDeleteDialogOpen(false);
    }

    function openDeleteDialog(docId: string) {
        setDocToDelete(docId);
        setIsDeleteDialogOpen(true);
    }


    async function handleDownload(docId: string, fileName: string) {
        const { data, errorMessage } = await apiClient.getDocument(course.id, docId);
        if (errorMessage || !data?.file_data) {
            toast.error("Failed to download document.");
            return;
        }

        const blob = b64toBlob(data.file_data, "application/pdf");
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        a.click();
        URL.revokeObjectURL(url);
    }

    function b64toBlob(base64: string, type = "application/pdf") {
        const binary = atob(base64);
        const array = Uint8Array.from(binary, (char) => char.charCodeAt(0));
        return new Blob([array], { type });
    }

    const totalPages = Math.max(1, Math.ceil(total / limit));
    const canPrev = page > 1;
    const canNext = page < totalPages;

    return (
        <>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="text-center sm:text-left">
                    <h1 className="text-2xl sm:text-3xl font-bold break-words">{course.name}</h1>
                    <p className="text-muted-foreground text-sm sm:text-base">
                        {course.code} • {course.semester}
                    </p>
                </div>
                <div className="flex justify-center sm:justify-end">
                    <Button
                        className="w-full sm:w-auto"
                        onClick={() => setIsAddDocumentOpen(true)}
                        disabled={loading}
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        Add Document
                    </Button>
                </div>
            </div>

            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg sm:text-xl">Course Documents</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <p className="text-center text-muted-foreground">Loading...</p>
                    ) : documents.length === 0 ? (
                        <p className="text-center text-muted-foreground">No documents uploaded yet.</p>
                    ) : (
                        <>
                            <div className="space-y-3">
                                {documents.map((doc) => (
                                    <div
                                        key={doc.id}
                                        className="flex items-center justify-between p-4 border rounded-lg"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                        <span className="text-xs font-medium">
                          {(doc.file_type || "FILE").toUpperCase()}
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
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => handleDownload(doc.id, doc.file_name)}
                                            >
                                                <Download className="h-4 w-4" />
                                            </Button>
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

            <Dialog open={isAddDocumentOpen} onOpenChange={setIsAddDocumentOpen}>
                <DialogContent className="max-w-md sm:max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Upload Documents for {course.name}</DialogTitle>
                    </DialogHeader>
                    <FileUpload onFilesSelected={setSelectedFiles} />
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

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent className="max-w-sm">
                    <DialogHeader>
                        <DialogTitle className="text-destructive">
                            Delete Document
                        </DialogTitle>
                    </DialogHeader>
                    <p className="text-sm text-muted-foreground">
                        Are you sure you want to permanently delete this document?
                        This action <strong>cannot be undone</strong>.
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