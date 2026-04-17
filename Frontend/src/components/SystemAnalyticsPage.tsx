import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import {
    BookOpen,
    BookText,
    BrainCircuit,
    FileText,
    GraduationCap,
    LineChart as LineChartIcon,
    MessageSquare,
    MessagesSquare,
    TrendingUp,
    UserSquare2,
    Users,
} from "lucide-react";

import { useApiClient } from "../clients/ApiClientContext.tsx";
import type {
    MetricBreakdownItem,
    SystemOverview,
    UsageTrendPoint,
} from "../clients/AnalyticsClient.ts";
import { StatCard } from "./StatCard.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card.tsx";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select.tsx";
import { UsageTrendChart } from "./charts/UsageTrendChart.tsx";
import { QueryDistributionPieChart } from "./charts/QueryDistributionPieChart.tsx";
import { RankedMetricList } from "./RankedMetricList.tsx";


const CHART_COLORS = ["#2563eb", "#14b8a6", "#f59e0b", "#ef4444", "#8b5cf6", "#0ea5e9"];

function topItems(items: MetricBreakdownItem[], count = 8) {
    return [...items]
        .filter((item) => item.count > 0)
        .sort((a, b) => b.count - a.count)
        .slice(0, count);
}

function formatPercentage(part: number, whole: number) {
    if (!whole) return "0%";
    return `${Math.round((part / whole) * 100)}%`;
}

export function SystemAnalyticsPage() {
    const { instructorId } = useParams<{ instructorId: string }>();
    const { analyticsClient } = useApiClient();

    const [selectedTimeRange, setSelectedTimeRange] = useState("30d");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [overview, setOverview] = useState<SystemOverview | null>(null);
    const [queryTrend, setQueryTrend] = useState<UsageTrendPoint[]>([]);
    const [documentsByCourse, setDocumentsByCourse] = useState<MetricBreakdownItem[]>([]);
    const [documentsByInstructor, setDocumentsByInstructor] = useState<MetricBreakdownItem[]>([]);
    const [coursesByInstructor, setCoursesByInstructor] = useState<MetricBreakdownItem[]>([]);
    const [queriesByCourse, setQueriesByCourse] = useState<MetricBreakdownItem[]>([]);

    useEffect(() => {
        if (!instructorId) return;

        let cancelled = false;
        setLoading(true);
        setError(null);

        (async () => {
            const [
                overviewRes,
                trendRes,
                docsCourseRes,
                docsInstructorRes,
                coursesInstructorRes,
                queriesCourseRes,
            ] = await Promise.all([
                analyticsClient.getSystemOverview(instructorId),
                analyticsClient.getSystemQueryTrend(instructorId, selectedTimeRange),
                analyticsClient.getDocumentsByCourse(instructorId),
                analyticsClient.getDocumentsByInstructor(instructorId),
                analyticsClient.getCoursesByInstructor(instructorId),
                analyticsClient.getQueriesByCourse(instructorId, selectedTimeRange),
            ]);

            if (cancelled) return;

            const errors = [
                overviewRes.errorMessage,
                trendRes.errorMessage,
                docsCourseRes.errorMessage,
                docsInstructorRes.errorMessage,
                coursesInstructorRes.errorMessage,
                queriesCourseRes.errorMessage,
            ].filter(Boolean);

            if (errors.length > 0) {
                setError(errors[0] || "Failed to load analytics.");
            } else {
                setOverview(overviewRes.data ?? null);
                setQueryTrend(trendRes.data ?? []);
                setDocumentsByCourse(docsCourseRes.data ?? []);
                setDocumentsByInstructor(docsInstructorRes.data ?? []);
                setCoursesByInstructor(coursesInstructorRes.data ?? []);
                setQueriesByCourse(queriesCourseRes.data ?? []);
            }

            setLoading(false);
        })();

        return () => {
            cancelled = true;
        };
    }, [analyticsClient, instructorId, selectedTimeRange]);

    const topDocumentCourses = useMemo(() => topItems(documentsByCourse, 6), [documentsByCourse]);
    const topDocumentInstructors = useMemo(() => topItems(documentsByInstructor, 6), [documentsByInstructor]);
    const topCourseOwners = useMemo(() => topItems(coursesByInstructor, 6), [coursesByInstructor]);
    const topQueriedCourses = useMemo(() => topItems(queriesByCourse, 5), [queriesByCourse]);

    const documentCourseList = useMemo(
        () =>
            topDocumentCourses.map((item) => ({
                label: item.courseName ?? "Unknown course",
                value: item.count,
                helper: "Uploaded documents in this course",
            })),
        [topDocumentCourses]
    );

    const documentInstructorList = useMemo(
        () =>
            topDocumentInstructors.map((item) => ({
                label: item.instructorName ?? "Unknown instructor",
                value: item.count,
                helper: "Documents uploaded across owned courses",
            })),
        [topDocumentInstructors]
    );

    const coursesInstructorList = useMemo(
        () =>
            topCourseOwners.map((item) => ({
                label: item.instructorName ?? "Unknown instructor",
                value: item.count,
                helper: "Courses created in the system",
            })),
        [topCourseOwners]
    );

    const queryShareData = useMemo(
        () =>
            topItems(queriesByCourse, 6).map((item, index) => ({
                name: item.courseName ?? "Unknown course",
                value: item.count,
                color: CHART_COLORS[index % CHART_COLORS.length],
            })),
        [queriesByCourse]
    );

    const totalQueriesInRange = topQueriedCourses.reduce((sum, item) => sum + item.count, 0);
    const coursesWithDocuments = documentsByCourse.filter((item) => item.count > 0).length;
    const activeCourses = queriesByCourse.filter((item) => item.count > 0).length;
    const activeContentInstructors = documentsByInstructor.filter((item) => item.count > 0).length;
    const mostQueriedCourse = topQueriedCourses[0];
    const mostContentRichCourse = topDocumentCourses[0];
    const mostContentActiveInstructor = topDocumentInstructors[0];
    const peakTrendPoint = [...queryTrend].sort((a, b) => b.queries - a.queries)[0];
    const activeQueryDays = queryTrend.filter((point) => point.queries > 0).length;
    const averageDailyQueries = queryTrend.length > 0
        ? Math.round(queryTrend.reduce((sum, point) => sum + point.queries, 0) / queryTrend.length)
        : 0;
    const averageDailyUsers = queryTrend.length > 0
        ? Math.round(queryTrend.reduce((sum, point) => sum + point.uniqueUsers, 0) / queryTrend.length)
        : 0;
    const averageDocumentsPerActiveInstructor = activeContentInstructors > 0
        ? Math.round((documentsByInstructor.reduce((sum, item) => sum + item.count, 0) / activeContentInstructors) * 10) / 10
        : 0;

    const insightCards = [
        {
            label: "Most Queried Course",
            value: mostQueriedCourse?.courseName ?? "No activity yet",
            subtext: mostQueriedCourse ? `${mostQueriedCourse.count.toLocaleString()} queries in selected range` : "Waiting for query data",
            icon: BrainCircuit,
        },
        {
            label: "Most Content-Rich Course",
            value: mostContentRichCourse?.courseName ?? "No documents yet",
            subtext: mostContentRichCourse ? `${mostContentRichCourse.count.toLocaleString()} uploaded documents` : "Waiting for document uploads",
            icon: BookText,
        },
        {
            label: "Leading Content Contributor",
            value: mostContentActiveInstructor?.instructorName ?? "No instructor activity",
            subtext: mostContentActiveInstructor ? `${mostContentActiveInstructor.count.toLocaleString()} documents across owned courses` : "Waiting for instructor uploads",
            icon: UserSquare2,
        },
        {
            label: "Peak Daily AI Demand",
            value: peakTrendPoint ? new Date(peakTrendPoint.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "No trend yet",
            subtext: peakTrendPoint ? `${peakTrendPoint.queries.toLocaleString()} queries on the busiest day` : "Waiting for daily usage data",
            icon: TrendingUp,
        },
    ];

    return (
        <div className="space-y-8">
            <div className="rounded-[2rem] border bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(20,184,166,0.12),_transparent_28%),linear-gradient(135deg,_rgba(248,250,252,0.94),_rgba(255,255,255,1))] p-6 shadow-[0_24px_60px_-30px_rgba(15,23,42,0.35)] sm:p-8 dark:bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(20,184,166,0.18),_transparent_28%),linear-gradient(135deg,_rgba(2,6,23,0.95),_rgba(15,23,42,0.98))]">
                <div className="flex flex-col gap-8 xl:flex-row xl:items-end xl:justify-between">
                    <div className="max-w-4xl space-y-4">
                        <div className="space-y-3">
                            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
                                CourseGPT Platform Overview
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-muted-foreground sm:text-lg">
                                A system-wide view of platform scale, content health, and how students are actually using the AI assistant across courses.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <div className="rounded-2xl border bg-background/70 px-4 py-3 backdrop-blur">
                                <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Content Coverage</p>
                                <p className="mt-1 text-lg font-semibold">
                                    {loading ? "—" : formatPercentage(coursesWithDocuments, overview?.totalCourses ?? 0)}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    of courses have uploaded documents
                                </p>
                            </div>
                            <div className="rounded-2xl border bg-background/70 px-4 py-3 backdrop-blur">
                                <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Active Courses</p>
                                <p className="mt-1 text-lg font-semibold">
                                    {loading ? "—" : activeCourses.toLocaleString()}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    courses generated AI traffic in this range
                                </p>
                            </div>
                            <div className="rounded-2xl border bg-background/70 px-4 py-3 backdrop-blur">
                                <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Query Concentration</p>
                                <p className="mt-1 text-lg font-semibold">
                                    {loading ? "—" : formatPercentage(mostQueriedCourse?.count ?? 0, totalQueriesInRange)}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    of AI demand comes from the top course
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col gap-3 sm:flex-row xl:flex-col">
                        <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                            <SelectTrigger className="w-44 rounded-2xl bg-background/80 shadow-sm">
                                <SelectValue placeholder="Time range" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="7d">Last 7 days</SelectItem>
                                <SelectItem value="30d">Last 30 days</SelectItem>
                                <SelectItem value="90d">Last 90 days</SelectItem>
                                <SelectItem value="1y">Last year</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
            </div>

            {error && (
                <Card className="border-destructive/30">
                    <CardContent className="pt-6 text-sm text-destructive">
                        {error}
                    </CardContent>
                </Card>
            )}

            <section className="space-y-4">
                <div>
                    <h2 className="text-xl font-semibold">Platform Snapshot</h2>
                    <p className="text-sm text-muted-foreground">
                        These metrics show how large the system is and how much AI activity it has processed.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                    <StatCard value={loading ? "—" : overview?.totalDocuments?.toLocaleString() ?? "0"} label="Total Documents" icon={FileText} className="bg-gradient-to-br from-white to-slate-50 shadow-sm dark:from-slate-950 dark:to-slate-900" />
                    <StatCard value={loading ? "—" : overview?.totalCourses?.toLocaleString() ?? "0"} label="Total Courses" icon={BookOpen} className="bg-gradient-to-br from-white to-slate-50 shadow-sm dark:from-slate-950 dark:to-slate-900" />
                    <StatCard value={loading ? "—" : overview?.totalInstructors?.toLocaleString() ?? "0"} label="Total Instructors" icon={UserSquare2} className="bg-gradient-to-br from-white to-slate-50 shadow-sm dark:from-slate-950 dark:to-slate-900" />
                    <StatCard value={loading ? "—" : overview?.totalStudents?.toLocaleString() ?? "0"} label="Total Students" icon={Users} className="bg-gradient-to-br from-white to-slate-50 shadow-sm dark:from-slate-950 dark:to-slate-900" />
                    <StatCard value={loading ? "—" : overview?.totalQueries?.toLocaleString() ?? "0"} label="Total AI Queries" icon={MessageSquare} className="bg-gradient-to-br from-white to-slate-50 shadow-sm dark:from-slate-950 dark:to-slate-900" />
                    <StatCard value={loading ? "—" : overview?.totalFeedback?.toLocaleString() ?? "0"} label="Feedback Entries" icon={MessagesSquare} className="bg-gradient-to-br from-white to-slate-50 shadow-sm dark:from-slate-950 dark:to-slate-900" />
                </div>
            </section>

            <section className="space-y-4">
                <div>
                    <h2 className="text-xl font-semibold">Operational Insights</h2>
                    <p className="text-sm text-muted-foreground">
                        These derived signals are meant to be more useful than raw averages alone.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-4 xl:grid-cols-4">
                    {insightCards.map(({ label, value, subtext, icon: Icon }) => (
                        <Card key={label} className="overflow-hidden border shadow-sm">
                            <CardContent className="relative pt-6">
                                <div className="absolute right-4 top-4 rounded-full bg-primary/10 p-2 text-primary">
                                    <Icon className="h-4 w-4" />
                                </div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                                    {label}
                                </p>
                                <p className="mt-6 line-clamp-2 text-2xl font-bold leading-tight">
                                    {loading ? "—" : value}
                                </p>
                                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                    {loading ? "Loading insight..." : subtext}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                    <Card className="shadow-sm">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base">Average Documents per Course</CardTitle>
                            <CardDescription>Content density across the platform</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-3xl font-bold">{loading ? "—" : overview?.averageDocumentsPerCourse ?? 0}</p>
                        </CardContent>
                    </Card>
                    <Card className="shadow-sm">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base">Average Courses per Instructor</CardTitle>
                            <CardDescription>Average instructor ownership footprint</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-3xl font-bold">{loading ? "—" : overview?.averageCoursesPerInstructor ?? 0}</p>
                        </CardContent>
                    </Card>
                    <Card className="shadow-sm">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base">Average Queries per Course</CardTitle>
                            <CardDescription>System-wide AI demand intensity</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-3xl font-bold">{loading ? "—" : overview?.averageQueriesPerCourse ?? 0}</p>
                        </CardContent>
                    </Card>
                    <Card className="shadow-sm">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base">Avg. Documents per Active Instructor</CardTitle>
                            <CardDescription>Content depth among instructors who uploaded material</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-3xl font-bold">{loading ? "—" : averageDocumentsPerActiveInstructor}</p>
                        </CardContent>
                    </Card>
                </div>
            </section>

            <section className="space-y-4">
                <div>
                    <h2 className="text-xl font-semibold">AI Usage Trend</h2>
                    <p className="text-sm text-muted-foreground">
                        A line chart is the right fit here because the key question is how usage changes over time, not just which category is biggest.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_0.55fr]">
                    <Card className="shadow-sm">
                        <CardHeader>
                            <CardTitle>AI Queries Over Time</CardTitle>
                            <CardDescription>
                                Daily query volume and unique student usage across the whole platform
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <UsageTrendChart data={queryTrend} height={220} />
                        </CardContent>
                    </Card>

                    <Card className="shadow-sm">
                        <CardHeader>
                            <CardTitle>Trend Summary</CardTitle>
                            <CardDescription>Compact reading of the selected time window</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="rounded-2xl border px-4 py-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Average daily queries</p>
                                <p className="mt-1 text-2xl font-bold">{loading ? "—" : averageDailyQueries}</p>
                            </div>
                            <div className="rounded-2xl border px-4 py-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Average daily active students</p>
                                <p className="mt-1 text-2xl font-bold">{loading ? "—" : averageDailyUsers}</p>
                            </div>
                            <div className="rounded-2xl border px-4 py-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Days with query activity</p>
                                <p className="mt-1 text-2xl font-bold">{loading ? "—" : activeQueryDays}</p>
                            </div>
                            <div className="rounded-2xl border bg-primary/5 px-4 py-4">
                                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-primary">
                                    <LineChartIcon className="h-4 w-4" />
                                    Busiest day
                                </p>
                                <p className="mt-1 text-lg font-semibold">
                                    {loading
                                        ? "—"
                                        : peakTrendPoint
                                            ? `${new Date(peakTrendPoint.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })} · ${peakTrendPoint.queries} queries`
                                            : "No usage yet"}
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </section>

            <section className="space-y-4">
                <div>
                    <h2 className="text-xl font-semibold">Content Footprint</h2>
                    <p className="text-sm text-muted-foreground">
                        These comparisons help show where knowledge is concentrated and where the system may need more uploaded material.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
                    <Card className="shadow-sm">
                        <CardHeader>
                            <CardTitle>Documents per Course</CardTitle>
                            <CardDescription>Ranked view of which courses have the most uploaded material</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <RankedMetricList
                                items={documentCourseList}
                                valueLabel="documents"
                                accentClassName="bg-blue-600"
                                emptyMessage="No course documents uploaded yet."
                                description="Each row ranks a course by uploaded material. The bar shows the course's relative document volume compared with the other displayed courses."
                            />
                        </CardContent>
                    </Card>

                    <Card className="shadow-sm">
                        <CardHeader>
                            <CardTitle>Documents per Instructor</CardTitle>
                            <CardDescription>Ranked view of who is contributing the most content</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <RankedMetricList
                                items={documentInstructorList}
                                valueLabel="documents"
                                accentClassName="bg-teal-600"
                                emptyMessage="No instructor document activity yet."
                                description="Each row ranks an instructor by the amount of uploaded content across their owned courses. Longer bars mean a larger share of the displayed content footprint."
                            />
                        </CardContent>
                    </Card>

                    <Card className="shadow-sm xl:col-span-2">
                        <CardHeader>
                            <CardTitle>Courses per Instructor</CardTitle>
                            <CardDescription>Ranked view of instructor ownership across the platform</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <RankedMetricList
                                items={coursesInstructorList}
                                valueLabel="courses"
                                accentClassName="bg-amber-700"
                                emptyMessage="No instructor course ownership data yet."
                                description="Each row ranks instructor ownership in the system. The bar shows the instructor's relative share of the displayed course count."
                            />
                        </CardContent>
                    </Card>
                </div>
            </section>

            <section className="space-y-4">
                <div>
                    <h2 className="text-xl font-semibold">AI Demand by Course</h2>
                    <p className="text-sm text-muted-foreground">
                        This section shows where the assistant is being used most heavily and how concentrated that demand is.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.2fr_0.8fr]">
                    <Card className="shadow-sm">
                        <CardHeader>
                            <CardTitle>Query Share by Course</CardTitle>
                            <CardDescription>Relative share of AI traffic among the most active courses</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <QueryDistributionPieChart data={queryShareData} />
                        </CardContent>
                    </Card>

                    <Card className="shadow-sm">
                        <CardHeader>
                            <CardTitle>Top Queried Courses</CardTitle>
                            <CardDescription>Ranked by AI usage in the selected window</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {loading ? (
                                <p className="text-sm text-muted-foreground">Loading…</p>
                            ) : topQueriedCourses.length === 0 ? (
                                <p className="text-sm italic text-muted-foreground">No AI query activity recorded yet.</p>
                            ) : (
                                <ul className="space-y-3">
                                    {topQueriedCourses.map((item, index) => (
                                        <li
                                            key={item.courseId ?? item.courseName}
                                            className="flex items-center justify-between gap-4 rounded-2xl border bg-slate-50/70 px-4 py-4 dark:bg-slate-900/60"
                                        >
                                            <div className="flex min-w-0 items-center gap-3">
                                                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 font-semibold text-primary">
                                                    {index + 1}
                                                </div>
                                                <div className="min-w-0">
                                                    <p className="truncate font-medium">{item.courseName ?? "Unknown course"}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {formatPercentage(item.count, totalQueriesInRange)} of query traffic
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2 font-semibold text-primary">
                                                <TrendingUp className="h-4 w-4" />
                                                <span>{item.count.toLocaleString()}</span>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </section>

            <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1.1fr_0.9fr]">
                <Card className="shadow-sm">
                    <CardHeader>
                        <CardTitle>How to Read This Dashboard</CardTitle>
                        <CardDescription>What each section is telling you operationally</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm leading-7 text-muted-foreground">
                        <p>
                            <GraduationCap className="mr-2 inline h-4 w-4 text-primary" />
                            The top metrics answer how large the platform is right now and whether the system has enough content relative to its number of courses.
                        </p>
                        <p>
                            <MessageSquare className="mr-2 inline h-4 w-4 text-primary" />
                            The trend chart answers whether AI usage is rising, falling, or clustered around a few high-demand days.
                        </p>
                        <p>
                            <FileText className="mr-2 inline h-4 w-4 text-primary" />
                            The content charts answer whether uploaded documents are evenly distributed or concentrated in only a few courses or instructors.
                        </p>
                        <p>
                            <BookText className="mr-2 inline h-4 w-4 text-primary" />
                            The AI demand section answers which courses are really leaning on the assistant, which helps prioritize future content uploads and support.
                        </p>
                    </CardContent>
                </Card>

                <Card className="shadow-sm">
                    <CardHeader>
                        <CardTitle>Quick Health Indicators</CardTitle>
                        <CardDescription>Fast signals worth tracking over time</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="rounded-2xl border px-4 py-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Courses with documents</p>
                            <p className="mt-1 text-2xl font-bold">{loading ? "—" : `${coursesWithDocuments}/${overview?.totalCourses ?? 0}`}</p>
                        </div>
                        <div className="rounded-2xl border px-4 py-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Courses active in selected range</p>
                            <p className="mt-1 text-2xl font-bold">{loading ? "—" : activeCourses}</p>
                        </div>
                        <div className="rounded-2xl border px-4 py-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Active instructors with content</p>
                            <p className="mt-1 text-2xl font-bold">{loading ? "—" : activeContentInstructors}</p>
                        </div>
                        <div className="rounded-2xl border px-4 py-4">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Total queries in selected range</p>
                            <p className="mt-1 text-2xl font-bold">{loading ? "—" : totalQueriesInRange.toLocaleString()}</p>
                        </div>
                    </CardContent>
                </Card>
            </section>
        </div>
    );
}
