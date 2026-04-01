import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext";
import type { TopQuestionsItem } from "../clients/AnalyticsClient";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { HelpCircle, ArrowLeft } from "lucide-react";

interface CourseAllQuestionsPageProps {
    course: { name: string; id?: string };
}

export function CourseAllQuestionsPage({ course }: CourseAllQuestionsPageProps) {
    const [questions, setQuestions] = useState<TopQuestionsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const { analyticsClient } = useApiClient();
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
            const res = await analyticsClient.getTopQuestions(courseId, 100);

            if (cancelled) return;

            if ("errorMessage" in res && res.errorMessage) {
                setError(res.errorMessage);
                setQuestions([]);
            } else if (res.data) {
                setQuestions(res.data);
            } else {
                setQuestions([]);
            }
            setLoading(false);
        })();

        return () => {
            cancelled = true;
        };
    }, [analyticsClient, courseId]);

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
                        Showing up to the most recent 100 questions.
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
                            {questions.map((item, index) => (
                                <li
                                    key={`${item.queryText}-${index}`}
                                    className="border-b border-border pb-3 last:border-0"
                                >
                                    <div className="flex justify-between gap-4">
                                        <span className="font-medium text-sm flex-1 min-w-0">
                                            {item.queryText}
                                        </span>
                                        <span className="text-xs text-muted-foreground shrink-0">
                                            {item.count} {item.count === 1 ? "time" : "times"}
                                        </span>
                                    </div>
                                    {item.answer && (
                                        <p className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">
                                            {item.answer}
                                        </p>
                                    )}
                                </li>
                            ))}
                        </ul>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

