import { useEffect, useState } from "react";
import { useWebSocketClient } from "../clients/WebSocketClientContext";
import { Loader2, XCircle, Eye, Download, Trash2 } from "lucide-react";
import { Button } from "./ui/button";

type DocStatus = "PROCESSING" | "COMPLETED" | "FAILED";

interface DocumentActionsProps {
    courseId: string;
    doc: any; // includes id, can_preview, file_name, etc.
    onPreview: () => void;
    onDownload: () => void;
    onDelete: () => void;
}

export function DocumentActions({
    courseId,
    doc,
    onPreview,
    onDownload,
    onDelete
}: DocumentActionsProps) {
    const wsClient = useWebSocketClient();
    
    const [status, setStatus] = useState<DocStatus>(doc.processing_status);

    const canUseFile = status === "COMPLETED";

    useEffect(() => {
        const sub = wsClient.subscribeCourseDocuments(courseId, (msg) => {
            if (msg?.event === "processing_status_changed" && msg.doc_id === doc.id) {
                setStatus(msg.status as DocStatus);
            }
        });

        return () => sub.unsubscribe();
    }, [courseId, doc.id, wsClient]);

    function renderStatusIcon() {
        if (status === "PROCESSING") {
            return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
        }
        if (status === "FAILED") {
            return <XCircle className="h-5 w-5 text-red-600" />;
        }
        return null;
    }

    return (
        <div className="flex items-center gap-2">
            {renderStatusIcon()}

            {/* Preview (only if completed AND previewable) */}
            {canUseFile && doc.can_preview && (
                <Button variant="ghost" size="sm" onClick={onPreview}>
                    <Eye className="h-4 w-4" />
                </Button>
            )}

            {/* Download (only completed) */}
            {canUseFile && (
                <Button variant="ghost" size="sm" onClick={onDownload}>
                    <Download className="h-4 w-4" />
                </Button>
            )}

            {/* Delete (always available) */}
            <Button variant="ghost" size="sm" onClick={onDelete}>
                <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
        </div>
    );
}
