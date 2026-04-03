import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext";
import type { CourseQueryRecord } from "../clients/QueryClient";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { HelpCircle, ArrowLeft } from "lucide-react";

const LIST_LIMIT = 1000;

// function formatAskedAt(iso: string | undefined): string | null {
//     if (!iso) return null;
//     const d = new Date(iso);
//     return Number.isNaN(d.getTime()) ? null : d.toLocaleString();
// }

interface CourseAllQuestionsPageProps {
    course: { name: string; id?: string };
}

function formatDateTimeDdMmYyyyHhMm(iso: string | undefined): string | null {
    if (!iso) return null;
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return null;
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    const h24 = d.getHours();
    const h12 = h24 % 12 || 12;
    const ampm = h24 >= 12 ? "PM" : "AM";
    const hh = String(h12).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    return `${dd}/${mm}/${yyyy} ${hh}:${min} ${ampm}`;
}

export function CourseAllQuestionsPage({ course }: CourseAllQuestionsPageProps) {
    const [questions, setQuestions] = useState<CourseQueryRecord[]>([]);
    const [totalCount, setTotalCount] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const { queryClient } = useApiClient();
    const navigate = useNavigate();
    const courseId = course.id;

    useEffect(() => {
        let cancelled = false;
        if (!courseId) {
            setError("Course ID is missing.");
            setLoading(false);
            return;
        }

        (async () => {
            setLoading(true);
            setError(null);
            const res = await queryClient.getCourseQueries(courseId, {
                limit: LIST_LIMIT,
                offset: 0,
                orderBy: "asked_at",
                orderDir: "desc",
            });

            if (cancelled) return;

            if ("errorMessage" in res && res.errorMessage) {
                setError(res.errorMessage);
                setQuestions([]);
                setTotalCount(null);
            } else if (res.data) {
                setQuestions(res.data.queries ?? []);
                setTotalCount(res.data.total ?? res.data.queries?.length ?? 0);
            } else {
                setQuestions([]);
                setTotalCount(null);
            }
            setLoading(false);
        })();

        return () => {
            cancelled = true;
        };
    }, [queryClient, courseId]);

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between gap-2">
                <div>
                    <h1 className="text-2xl font-bold">All Questions &amp; Answers</h1>
                    <p className="text-sm text-muted-foreground">
                        Full list of questions students have asked in {course.name}.
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/courses/${courseId}/analytics`)}
                >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to Analytics
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <HelpCircle className="h-5 w-5" />
                        Questions and Answers
                    </CardTitle>
                    <CardDescription>
                        {totalCount != null
                            ? totalCount > LIST_LIMIT
                                ? `Showing the ${LIST_LIMIT} most recent of ${totalCount} Q&A entries.`
                                : `Showing ${totalCount} Q&A ${totalCount === 1 ? "entry" : "entries"}.`
                            : `Showing up to ${LIST_LIMIT} most recent Q&A entries.`}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <p className="text-sm text-muted-foreground">Loading…</p>
                    ) : error ? (
                        <p className="text-sm text-destructive">{error}</p>
                    ) : questions.length === 0 ? (
                        <p className="text-sm text-muted-foreground">
                            No questions recorded yet.
                        </p>
                    ) : (
                        <ul className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                            {questions.map((item) => {
                                const when = formatDateTimeDdMmYyyyHhMm(item.asked_at);
                                return (
                                <li
                                    key={item.id}
                                    className="border-b border-border pb-3 last:border-0"
                                >
                                    <div className="flex justify-between gap-4">
                                        <span className="font-medium text-sm flex-1 min-w-0">
                                            {item.query_text}
                                        </span>
                                        {when && (
                                            <span className="text-xs text-muted-foreground shrink-0">
                                                {when}
                                            </span>
                                        )}
                                    </div>
                                    {item.response_text && (
                                        <p className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">
                                            {item.response_text}
                                        </p>
                                    )}
                                </li>
                                );
                            })}
                        </ul>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

