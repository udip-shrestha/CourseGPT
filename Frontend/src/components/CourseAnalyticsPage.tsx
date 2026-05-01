import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    MessageSquare, TrendingUp, Activity, HelpCircle,
    FileText,
    GraduationCap, Sparkles, Tags
} from "lucide-react";

import { useApiClient } from "../clients/ApiClientContext.tsx";
import type {
    UsageTrendPoint,
    TopQuestionsItem,
    TopKeywordsItem,
    CourseSatisfaction,
    AnswerFeedbackItem
} from "../clients/AnalyticsClient";

import { StatCard } from "./StatCard.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select.tsx";
import { Button } from "./ui/button.tsx";
import { UsageTrendChart } from "./charts/UsageTrendChart.tsx";
import { CourseBarChart } from "./charts/CoursebarChart.tsx";

const STOPWORDS = new Set([
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
    "what", "who", "where", "when", "why", "how", "to", "of", "in",
    "for", "on", "with", "at", "by", "from", "up", "about", "into",
    "over", "after", "your", "mine", "my", "me", "you", "they", "them",
    "this", "that", "these", "those", "it", "its", "it's"
]);

const CONCEPT_MAP: Record<string, string> = {
    "iptables": "Networking", "routing": "Networking", "ip": "Networking", "port": "Networking", "tcp": "Networking",
    "mutex": "Concurrency", "semaphore": "Concurrency", "goroutine": "Concurrency", "threads": "Concurrency",
    "pointer": "Memory Management", "memory": "Memory Management", "address": "Memory Management", "malloc": "Memory Management", "aliasing": "Memory Management",
    "kafka": "Distributed Systems", "distributed": "Distributed Systems", "microservices": "Distributed Systems",
    "docker": "DevOps/Cloud"
};

interface CourseAnalyticsPageProps {
    course: { name: string; id?: string; instructor_id?: string };
}

export function CourseAnalyticsPage({ course }: CourseAnalyticsPageProps) {
    const { courseId: routeCourseId } = useParams();
    const courseId = course.id ?? routeCourseId ?? "";
    const { analyticsClient } = useApiClient();
    const navigate = useNavigate();

    const [selectedTimeRange, setSelectedTimeRange] = useState("7d");
    const [loading, setLoading] = useState(true);

    const [usageTrend, setUsageTrend] = useState<UsageTrendPoint[]>([]);
    const [topQuestions, setTopQuestions] = useState<TopQuestionsItem[]>([]);
    const [topKeywords, setTopKeywords] = useState<TopKeywordsItem[]>([]);
    const [satisfactionData, setSatisfactionData] = useState<CourseSatisfaction | null>(null);
    const [feedbacks, setFeedbacks] = useState<AnswerFeedbackItem[]>([]);
    const [enrolledCount, setEnrolledCount] = useState(0);
    const [totalDocs, setTotalDocs] = useState(0);
    const [uniqueActiveCount, setUniqueActiveCount] = useState(0);

    const filteredKeywords = useMemo(() => {
        return topKeywords.filter(item => !STOPWORDS.has(item.keyword.toLowerCase()));
    }, [topKeywords]);

    const topicUsageData = useMemo(() => {
        const clusters: Record<string, number> = {};
        filteredKeywords.forEach(item => {
            const keyword = item.keyword.toLowerCase();
            const clusterName = CONCEPT_MAP[keyword] || (keyword.charAt(0).toUpperCase() + keyword.slice(1));
            clusters[clusterName] = (clusters[clusterName] || 0) + item.count;
        });
        return Object.entries(clusters)
            .map(([topic, queries]) => ({ topic, queries }))
            .sort((a, b) => b.queries - a.queries)
            .slice(0, 5);
    }, [filteredKeywords]);

    const unhelpfulQuestions = useMemo(() => {
        const unhelpfulQueryIds = new Set(
            feedbacks
                .filter(f => String(f.vote).toLowerCase() === "down")
                .map(f => f.query_id)
        );

        // Return top questions where students gave negative feedback
        // Uses @ts-ignore to allow check against query_id if it exists at runtime
        return topQuestions.filter(q =>
            unhelpfulQueryIds.has(q.queryText) ||
            // @ts-ignore
            unhelpfulQueryIds.has(q.query_id)
        );
    }, [feedbacks, topQuestions]);

    const engagementRate = useMemo(() => {
        if (enrolledCount === 0) return 0;
        return Math.round((uniqueActiveCount / enrolledCount) * 100);
    }, [uniqueActiveCount, enrolledCount]);

    useEffect(() => {
        if (!courseId) return;
        let cancelled = false;
        setLoading(true);

        (async () => {
            const [trendRes, qRes, keyRes, sCountRes, satRes, docCountRes, feedRes] = await Promise.all([
                analyticsClient.getUsageTrend(courseId, selectedTimeRange),
                analyticsClient.getTopQuestions(courseId, 10, selectedTimeRange),
                analyticsClient.getTopKeywords(courseId, 12, selectedTimeRange),
                analyticsClient.getStudentCount(courseId),
                analyticsClient.getCourseSatisfaction(courseId),
                analyticsClient.getDocumentCount(courseId),
                analyticsClient.getCourseAnswerFeedbacks(courseId, 100)
            ]);

            if (cancelled) return;

            if (trendRes.data) setUsageTrend(trendRes.data);
            if (qRes.data) setTopQuestions(qRes.data);
            if (keyRes.data) setTopKeywords(keyRes.data);
            if (sCountRes.data) setEnrolledCount(sCountRes.data.student_count);
            if (satRes.data) setSatisfactionData(satRes.data);
            if (docCountRes.data !== undefined) setTotalDocs(docCountRes.data);

            if (feedRes.data && feedRes.data.answer_feedbacks) {
                setFeedbacks(feedRes.data.answer_feedbacks);
                const uniqueIds = new Set(feedRes.data.answer_feedbacks.map(f => f.student_id));
                setUniqueActiveCount(uniqueIds.size);
            }

            setLoading(false);
        })();
        return () => { cancelled = true; };
    }, [courseId, selectedTimeRange, analyticsClient]);

    return (
        <div className="space-y-8">
            {/* 1. HEADER */}
            <div className="rounded-[2.5rem] border bg-white dark:bg-slate-950 overflow-hidden relative shadow-sm border-slate-200 dark:border-slate-800 transition-colors">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.07),_transparent_40%)] pointer-events-none" />
                <div className="relative p-8 flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-primary font-bold uppercase tracking-widest text-xs">
                            <Sparkles className="h-4 w-4" /> Course Intelligence
                        </div>
                        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
                            Analyzing instructional activity, engagement, and student satisfaction.
                        </p>
                    </div>

                    <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                        <SelectTrigger className="w-44 h-11 rounded-2xl border-slate-400 dark:border-slate-600 bg-white dark:bg-slate-900 shadow-md font-bold text-slate-900 dark:text-slate-100 transition-all hover:border-primary">
                            <SelectValue placeholder="Select Range" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                            <SelectItem value="7d">Last 7 days</SelectItem>
                            <SelectItem value="30d">Last 30 days</SelectItem>
                            <SelectItem value="90d">Last 90 days</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* 2. STAT CARDS */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
                <StatCard value={loading ? "—" : enrolledCount.toLocaleString()} label="Enrolled Students" icon={GraduationCap} />
                <StatCard value={loading ? "—" : usageTrend.reduce((s, p) => s + p.queries, 0).toLocaleString()} label="Total Queries" icon={MessageSquare} />
                <StatCard value={loading ? "—" : `${engagementRate}%`} label="Engagement Rate" icon={Activity} />
                <StatCard value={loading ? "—" : totalDocs.toLocaleString()} label="Knowledge Base Files" icon={FileText} />

                <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-none">
                    <CardContent className="pt-6">
                        <div className="flex justify-between items-start mb-2">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Discord Sentiment</p>
                            <TrendingUp className="h-4 w-4 text-primary" />
                        </div>
                        <p className="text-2xl font-bold text-slate-900 dark:text-white">
                            {loading ? "—" : satisfactionData?.total_votes ? `${satisfactionData.satisfaction_score.toFixed(1)} / 5.0` : "No votes"}
                        </p>
                        {!loading && satisfactionData && satisfactionData.total_votes > 0 && (
                            <div className="mt-3 space-y-1">
                                <div className="flex h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                                    <div className="bg-green-500 transition-all duration-500" style={{ width: `${(satisfactionData.upvotes / satisfactionData.total_votes) * 100}%` }} />
                                    <div className="bg-red-500 transition-all duration-500" style={{ width: `${(satisfactionData.downvotes / satisfactionData.total_votes) * 100}%` }} />
                                </div>
                                <div className="flex justify-between text-[10px] font-bold uppercase">
                                    <span className="text-green-600">{satisfactionData.upvotes} Helpful</span>
                                    <span className="text-red-500">{satisfactionData.downvotes} Not Helpful</span>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* 3. TREND AND SUMMARY */}
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_0.55fr]">
                <Card className="shadow-sm border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <CardHeader><CardTitle>Interaction Trend</CardTitle></CardHeader>
                    <CardContent><UsageTrendChart data={usageTrend} height={320} /></CardContent>
                </Card>
                <div className="space-y-4">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground px-1">Trend Summary</h3>
                    <SummaryRow label="Avg. Daily Queries" value={usageTrend.length > 0 ? Math.round(usageTrend.reduce((s, p) => s + p.queries, 0) / usageTrend.length) : 0} />
                    <SummaryRow label="Verified Active Students" value={uniqueActiveCount} />
                    <SummaryRow label="Days with Activity" value={usageTrend.filter(p => p.queries > 0).length} />
                </div>
            </div>

            {/* 4. TOPICS (Concept Clusters) */}
            <div className="grid grid-cols-1 gap-6">
                <Card className="shadow-sm border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2"><Tags className="h-5 w-5 text-primary" /> Concept Clusters</CardTitle>
                        <CardDescription>Aggregating related keywords into parent instructional concepts</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {topicUsageData.length > 0 ? (
                            <CourseBarChart data={topicUsageData} xKey="topic" yKey="queries" />
                        ) : (
                            <p className="text-sm italic text-muted-foreground text-center py-10">No instructional data recorded.</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* 5. GAPS & FAQ */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <Card className="shadow-sm border-red-200 dark:border-red-900 bg-red-50/30 dark:bg-red-950/10">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-red-600">
                            <HelpCircle className="h-5 w-5" /> Potential Knowledge Gaps
                        </CardTitle>
                        <CardDescription>Questions students marked as "Not Helpful"</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-4">
                            {unhelpfulQuestions.length > 0 ? (
                                unhelpfulQuestions.slice(0, 4).map((q, i) => (
                                    <li key={i} className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-red-100 dark:border-red-800">
                                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{q.queryText}</p>
                                        <p className="text-[10px] mt-2 text-red-500 font-bold uppercase tracking-tighter">Action Required: Update Curriculum Docs</p>
                                    </li>
                                ))
                            ) : (
                                <p className="text-sm italic text-muted-foreground text-center py-6">No instructional gaps detected.</p>
                            )}
                        </ul>
                    </CardContent>
                </Card>

                <Card className="shadow-sm border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2"><MessageSquare className="h-5 w-5 text-primary" /> Top Questions</CardTitle>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/courses/${courseId}/questions`)}>View All</Button>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-4">
                            {topQuestions.slice(0, 4).map((q, i) => (
                                <li key={i} className="flex justify-between items-start gap-4 pb-3 border-b last:border-0 border-slate-100 dark:border-slate-800">
                                    <span className="text-sm font-medium leading-relaxed text-slate-900 dark:text-slate-100 line-clamp-2">{q.queryText}</span>
                                    <span className="text-xs font-bold px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md shrink-0">{q.count}×</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function SummaryRow({ label, value }: { label: string, value: any }) {
    return (
        <div className="rounded-[1.5rem] border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm">
            <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{label}</p>
            <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
        </div>
    );
}