import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    MessageSquare, TrendingUp, Activity, HelpCircle,
    FileText, BrainCircuit, LineChart as LineChartIcon, BookText,
    GraduationCap, MessagesSquare, Sparkles, Tags
} from "lucide-react";

import { useApiClient } from "../clients/ApiClientContext.tsx";
import type {
    UsageTrendPoint,
    TopQuestionsItem,
    TopKeywordsItem,
    CourseSatisfaction,
    DocumentUsageItem
} from "../clients/AnalyticsClient";

import { StatCard } from "./StatCard.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card.tsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select.tsx";
import { Button } from "./ui/button.tsx";
import { UsageTrendChart } from "./charts/UsageTrendChart.tsx";

// Filler words to filter out of the Top Keywords display
const STOPWORDS = new Set([
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
    "what", "who", "where", "when", "why", "how", "to", "of", "in",
    "for", "on", "with", "at", "by", "from", "up", "about", "into",
    "over", "after", "your", "mine", "my", "me", "you", "they", "them",
    "this", "that", "these", "those", "it", "its", "it's"
]);

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
    const [enrolledCount, setEnrolledCount] = useState(0);
    const [docUsage, setDocUsage] = useState<DocumentUsageItem[]>([]);
    const [totalDocs, setTotalDocs] = useState(0);

    const filteredKeywords = useMemo(() => {
        return topKeywords.filter(
            (item) => !STOPWORDS.has(item.keyword.toLowerCase())
        );
    }, [topKeywords]);

    const peakTrendPoint = useMemo(() =>
        [...usageTrend].sort((a, b) => b.queries - a.queries)[0], [usageTrend]);

    const averageDailyQueries = useMemo(() =>
        usageTrend.length > 0 ? Math.round(usageTrend.reduce((sum, p) => sum + p.queries, 0) / usageTrend.length) : 0, [usageTrend]);

    const averageDailyUsers = useMemo(() =>
        usageTrend.length > 0 ? Math.round(usageTrend.reduce((sum, p) => sum + p.uniqueUsers, 0) / usageTrend.length) : 0, [usageTrend]);

    useEffect(() => {
        if (!courseId) return;
        let cancelled = false;
        setLoading(true);

        (async () => {
            const [trendRes, qRes, keyRes, sCountRes, satRes, docUsageRes, overviewRes] = await Promise.all([
                analyticsClient.getUsageTrend(courseId, selectedTimeRange),
                analyticsClient.getTopQuestions(courseId, 5, selectedTimeRange),
                analyticsClient.getTopKeywords(courseId, 12, selectedTimeRange),
                analyticsClient.getStudentCount(courseId),
                analyticsClient.getCourseSatisfaction(courseId),
                analyticsClient.getCourseDocumentUsage(courseId),
                analyticsClient.getCourseOverview(courseId)
            ]);

            if (cancelled) return;

            if (trendRes.data) setUsageTrend(trendRes.data);
            if (qRes.data) setTopQuestions(qRes.data);
            if (keyRes.data) setTopKeywords(keyRes.data);
            if (sCountRes.data) setEnrolledCount(sCountRes.data.student_count);
            if (satRes.data) setSatisfactionData(satRes.data);
            if (docUsageRes.data) setDocUsage(docUsageRes.data);
            if (overviewRes.data) setTotalDocs(overviewRes.data.totalDocuments ?? 0);

            setLoading(false);
        })();
        return () => { cancelled = true; };
    }, [courseId, selectedTimeRange, analyticsClient]);

    return (
        <div className="space-y-8">
            {/* 1. PREMIUM HEADER WITH HIGH VISIBILITY */}
            <div className="rounded-[2.5rem] border bg-white dark:bg-slate-950 overflow-hidden relative shadow-sm border-slate-200 dark:border-slate-800 transition-colors">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.07),_transparent_40%)] pointer-events-none" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,_rgba(20,184,166,0.04),_transparent_40%)] pointer-events-none" />

                <div className="relative p-8 flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-primary font-bold uppercase tracking-widest text-xs">
                            <Sparkles className="h-4 w-4" /> Course Intelligence
                        </div>
                        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl text-slate-900 dark:text-white">
                            {course.name}
                        </h1>
                        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
                            Analyzing AI interactions, document utility, and student satisfaction metrics.
                        </p>
                    </div>

                    <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                        <SelectTrigger className="w-44 h-11 rounded-2xl border-slate-200 bg-white shadow-sm hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800 transition-all font-medium">
                            <SelectValue placeholder="Range" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl border-slate-200 dark:border-slate-800">
                            <SelectItem value="7d">Last 7 days</SelectItem>
                            <SelectItem value="30d">Last 30 days</SelectItem>
                            <SelectItem value="90d">Last 90 days</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* 2. STAT CARDS */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
                <StatCard value={loading ? "—" : enrolledCount.toLocaleString()} label="Enrolled Students" icon={GraduationCap} />
                <StatCard value={loading ? "—" : usageTrend.reduce((s, p) => s + p.queries, 0).toLocaleString()} label="Total Queries" icon={MessageSquare} />
                <StatCard value={loading ? "—" : totalDocs.toLocaleString()} label="Total Documents" icon={FileText} />
                <StatCard
                    value={loading ? "—" : satisfactionData?.total_votes ? `${satisfactionData.satisfaction_score.toFixed(1)} / 5.0` : "No votes"}
                    label="Avg. Satisfaction"
                    icon={TrendingUp}
                />
            </div>

            {/* 3. INSIGHT CARDS */}
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-4">
                <InsightCard
                    label="Peak AI Demand"
                    value={peakTrendPoint ? new Date(peakTrendPoint.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "N/A"}
                    subtext={peakTrendPoint ? `${peakTrendPoint.queries} queries on busiest day` : "No trend data"}
                    icon={Activity}
                />
                <InsightCard
                    label="Leading Document"
                    value={docUsage[0]?.documentName ?? "None"}
                    subtext={docUsage[0] ? `Answered ${docUsage[0].studentCount} students` : "No retrieval data"}
                    icon={BookText}
                />
                <InsightCard
                    label="Daily Momentum"
                    value={averageDailyQueries}
                    subtext="Avg. Questions per day"
                    icon={BrainCircuit}
                />
                <InsightCard
                    label="Total Feedback"
                    value={satisfactionData?.total_votes ?? 0}
                    subtext="Discord reactions received"
                    icon={MessagesSquare}
                />
            </div>

            {/* 4. TREND CHART + SUMMARY */}
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_0.55fr]">
                <Card className="shadow-sm border-slate-200 dark:border-slate-800">
                    <CardHeader>
                        <CardTitle>Usage Trend</CardTitle>
                        <CardDescription>Visualizing query volume vs unique student engagement</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <UsageTrendChart data={usageTrend} height={300} />
                    </CardContent>
                </Card>

                <div className="space-y-4">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground px-1">Trend Summary</h3>
                    <SummaryRow label="Daily Active Students" value={averageDailyUsers} />
                    <SummaryRow label="Days with Activity" value={usageTrend.filter(p => p.queries > 0).length} />
                    <div className="rounded-[1.5rem] border border-primary/20 bg-primary/5 p-5">
                        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-primary">
                            <LineChartIcon className="h-4 w-4" /> Busiest Day
                        </p>
                        <p className="mt-2 text-xl font-bold">
                            {peakTrendPoint ? `${peakTrendPoint.queries} Queries` : "—"}
                        </p>
                        <p className="text-xs text-primary/70">{peakTrendPoint ? new Date(peakTrendPoint.date).toLocaleDateString() : ""}</p>
                    </div>
                </div>
            </div>

            {/* 5. TOP KEYWORDS & FAQ */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <Card className="shadow-sm border-slate-200 dark:border-slate-800">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Tags className="h-5 w-5 text-primary" /> Top Keywords
                        </CardTitle>
                        <CardDescription>Most common topics in student questions</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loading ? <p className="text-sm text-muted-foreground">Loading...</p> : filteredKeywords.length === 0 ? (
                            <p className="text-sm italic text-muted-foreground">No keyword data yet.</p>
                        ) : (
                            <div className="flex flex-wrap gap-2">
                                {filteredKeywords.map((item, i) => (
                                    <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-sm">
                                        <span className="font-semibold text-primary">{item.keyword}</span>
                                        <span className="text-[10px] bg-slate-200 dark:bg-slate-800 px-1.5 py-0.5 rounded-md font-bold">{item.count}×</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card className="shadow-sm border-slate-200 dark:border-slate-800">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <HelpCircle className="h-5 w-5 text-primary" /> Frequent Questions
                            </CardTitle>
                            <CardDescription>Common student inquiries by count</CardDescription>
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/courses/${courseId}/questions`)}>View All</Button>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-4">
                            {topQuestions.map((q, i) => (
                                <li key={i} className="flex justify-between items-start gap-4 pb-3 border-b last:border-0 border-slate-100 dark:border-slate-800">
                                    <span className="text-sm font-medium leading-relaxed">{q.queryText}</span>
                                    <span className="text-xs font-bold px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md shrink-0">{q.count}×</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            </div>

            {/* 6. KNOWLEDGE BASE UTILIZATION */}
            <Card className="shadow-sm border-slate-200 dark:border-slate-800">
                <CardHeader>
                    <CardTitle>Knowledge Base Utilization</CardTitle>
                    <CardDescription>Documents answering the most student queries</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {loading ? <p className="text-sm text-muted-foreground">Loading...</p> : docUsage.length === 0 ? <p className="italic text-muted-foreground text-sm">No retrieval data available yet.</p> : (
                        docUsage.map((doc, i) => (
                            <div key={i} className="flex items-center justify-between p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                                <div className="flex items-center gap-4 min-w-0">
                                    <div className="h-10 w-10 shrink-0 flex items-center justify-center rounded-full bg-primary/10 text-primary font-bold">{i + 1}</div>
                                    <div className="truncate">
                                        <p className="font-semibold text-sm truncate">{doc.documentName}</p>
                                        <p className="text-xs text-muted-foreground">{doc.usagePercentage}% student reach</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-bold">{doc.studentCount}</p>
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">Students</p>
                                </div>
                            </div>
                        ))
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

// Internal Helper Components for the "Admin" Look
function InsightCard({ label, value, subtext, icon: Icon }: any) {
    return (
        <Card className="overflow-hidden border border-slate-200 dark:border-slate-800 shadow-none hover:border-primary/30 transition-colors bg-white dark:bg-slate-950">
            <CardContent className="pt-6">
                <div className="flex justify-between items-start mb-4">
                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">{label}</p>
                    <div className="p-2 bg-primary/5 rounded-lg text-primary"><Icon className="h-4 w-4" /></div>
                </div>
                <p className="text-2xl font-bold truncate text-slate-900 dark:text-white">{value}</p>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{subtext}</p>
            </CardContent>
        </Card>
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