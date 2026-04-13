import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext.tsx";
import type { CourseQueryRecord } from "../clients/QueryClient";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card.tsx";
import { Button } from "./ui/button.tsx";
import { HelpCircle, ArrowLeft, ChevronDown } from "lucide-react";

// Initial number of questions to show
const INITIAL_BATCH = 20;

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

interface CourseAllQuestionsPageProps {
    course: { name: string; id?: string };
}

export function CourseAllQuestionsPage({ course }: CourseAllQuestionsPageProps) {
    const [questions, setQuestions] = useState<CourseQueryRecord[]>([]);
    const [totalCount, setTotalCount] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Track how many items we are currently displaying
    const [visibleCount, setVisibleCount] = useState(INITIAL_BATCH);

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
            // We still fetch a healthy amount, but we only SHOW a slice of them
            const res = await queryClient.getCourseQueries(courseId, {
                limit: 1000,
                offset: 0,
                orderBy: "asked_at",
                orderDir: "desc",
            });

            if (cancelled) return;

            if ("errorMessage" in res && res.errorMessage) {
                setError(res.errorMessage);
            } else if (res.data) {
                setQuestions(res.data.queries ?? []);
                setTotalCount(res.data.total ?? res.data.queries?.length ?? 0);
            }
            setLoading(false);
        })();

        return () => { cancelled = true; };
    }, [queryClient, courseId]);

    // Function to "extend" the list
    const handleLoadMore = () => {
        setLoadingMore(true);
        // Simulate a tiny delay for better UX feel, then show 20 more
        setTimeout(() => {
            setVisibleCount((prev) => prev + 20);
            setLoadingMore(false);
        }, 300);
    };

    const displayedQuestions = questions.slice(0, visibleCount);
    const hasMore = questions.length > visibleCount;

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
                            ? `Showing ${displayedQuestions.length} of ${totalCount} Q&A entries.`
                            : "Loading entries..."}
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
                        <div className="space-y-6">
                            <ul className="space-y-4 max-h-[65vh] overflow-y-auto pr-2 custom-scrollbar">
                                {displayedQuestions.map((item) => {
                                    const when = formatDateTimeDdMmYyyyHhMm(item.asked_at);
                                    return (
                                        <li
                                            key={item.id}
                                            className="border-b border-border pb-4 last:border-0 group"
                                        >
                                            <div className="flex justify-between gap-4">
                                                <span className="font-semibold text-sm flex-1 min-w-0 group-hover:text-primary transition-colors">
                                                    {item.query_text}
                                                </span>
                                                {when && (
                                                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground shrink-0 mt-1">
                                                        {when}
                                                    </span>
                                                )}
                                            </div>
                                            {item.response_text && (
                                                <div className="mt-2 p-3 bg-muted/30 rounded-md border-l-2 border-primary/20">
                                                    <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                                                        {item.response_text}
                                                    </p>
                                                </div>
                                            )}
                                        </li>
                                    );
                                })}
                            </ul>

                            {hasMore && (
                                <div className="flex justify-center pt-2 border-t border-border">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="text-muted-foreground hover:text-primary"
                                        onClick={handleLoadMore}
                                        disabled={loadingMore}
                                    >
                                        {loadingMore ? "Expanding..." : "See More Questions"}
                                        <ChevronDown className={`ml-2 h-4 w-4 ${loadingMore ? 'animate-pulse' : ''}`} />
                                    </Button>
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}