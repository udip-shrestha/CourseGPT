import { useState, useEffect, useMemo } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./ui/card.tsx";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select.tsx";
import { Button } from "./ui/button.tsx";
import { Users, MessageSquare, TrendingUp, Activity, HelpCircle } from "lucide-react";
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid
} from "recharts";
import { useNavigate, useParams } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext.tsx";
import type { OverviewSummary, UsageTrendPoint, QueryDistributionItem, TopQuestionsItem, TopKeywordsItem } from "../clients/AnalyticsClient";
import { StatCard } from "./StatCard.tsx";
import { CourseBarChart } from "./charts/CoursebarcChart.tsx";

const CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

interface CourseAnalyticsPageProps {
    course: { name: string; id?: string; instructor_id?: string };
}

// Local Component for Trend Chart
function UsageTrendChart({ data }: { data: UsageTrendPoint[] }) {
    const queryTrendColor = useMemo(() => {
        if (data.length < 2) return "#3b82f6";
        return data[data.length - 1].queries >= data[0].queries ? "#10b981" : "#ef4444";
    }, [data]);

    const userTrendColor = useMemo(() => {
        if (data.length < 2) return "#94a3b8";
        return data[data.length - 1].uniqueUsers >= data[0].uniqueUsers ? "#059669" : "#dc2626";
    }, [data]);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.2} />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} />
                <Legend />
                <Line type="monotone" dataKey="queries" stroke={queryTrendColor} strokeWidth={3} dot={false} name="Total Queries" />
                <Line type="monotone" dataKey="uniqueUsers" stroke={userTrendColor} strokeWidth={2} strokeDasharray="5 5" dot={false} name="Unique Users (Students)" />
            </LineChart>
        </ResponsiveContainer>
    );
}

export function CourseAnalyticsPage({ course }: CourseAnalyticsPageProps) {
    const [selectedTimeRange, setSelectedTimeRange] = useState("7d");
    const [loading, setLoading] = useState(true);
    const [overviewSummary, setOverviewSummary] = useState<OverviewSummary | null>(null);
    const [usageTrend, setUsageTrend] = useState<UsageTrendPoint[]>([]);
    const [topQuestions, setTopQuestions] = useState<TopQuestionsItem[]>([]);
    const [queryDistribution, setQueryDistribution] = useState<QueryDistributionItem[]>([]);
    const [topKeywords, setTopKeywords] = useState<TopKeywordsItem[]>([]);
    const [totalCount, setTotalCount] = useState<number | null>(null);
    const [enrolledCount, setEnrolledCount] = useState<number>(0);

    const { analyticsClient, queryClient } = useApiClient();
    const navigate = useNavigate();
    const { courseId: routeCourseId } = useParams();
    const courseId = course.id ?? routeCourseId ?? "";
    const instructorId = course.instructor_id;

    const engagementScore = useMemo(() => {
        const activeUsers = overviewSummary?.activeUsers ?? 0;
        const queries = totalCount ?? overviewSummary?.totalQueries ?? 0;
        if (enrolledCount === 0) return 0;
        const reach = activeUsers / enrolledCount;
        const intensity = Math.min((queries / enrolledCount) / 10, 1);
        return Math.round((reach * 0.7 + intensity * 0.3) * 100);
    }, [overviewSummary, totalCount, enrolledCount]);

    const totalChatbotQueries = totalCount ?? overviewSummary?.totalQueries ?? 0;

    const courseUsageData = [{
        courseId: courseId,
        courseName: course.name,
        courseCode: course.name.slice(0, 8),
        activeUsers: overviewSummary?.activeUsers ?? 0,
        totalUsers: enrolledCount,
        chatbotQueries: totalChatbotQueries,
        averageResponseTime: 0,
        satisfaction: overviewSummary?.averageSatisfaction ?? 0,
    }];

    useEffect(() => {
        if (!courseId) return;
        let cancelled = false;
        setLoading(true);
        (async () => {
            const [ovRes, trendRes, qRes, distRes, keyRes, queriesRes, sCountRes] = await Promise.all([
                analyticsClient.getOverviewSummary(courseId, selectedTimeRange),
                analyticsClient.getUsageTrend(courseId, selectedTimeRange),
                analyticsClient.getTopQuestions(courseId, 10, selectedTimeRange),
                instructorId ? analyticsClient.getQueryDistribution(instructorId, selectedTimeRange) : Promise.resolve({ data: undefined }),
                analyticsClient.topKeywords(courseId, 5, selectedTimeRange),
                queryClient.getCourseQueries(courseId, { limit: 1, offset: 0 }),
                analyticsClient.getStudentCount(courseId)
            ]);

            if (cancelled) return;
            if (sCountRes.data) setEnrolledCount(sCountRes.data.student_count ?? 0);
            if (ovRes.data) setOverviewSummary(ovRes.data);
            if (trendRes.data) setUsageTrend(trendRes.data);
            if (qRes.data) setTopQuestions(qRes.data);
            if (distRes.data) setQueryDistribution(distRes.data);
            if (keyRes.data) setTopKeywords(keyRes.data);
            if (queriesRes.data) setTotalCount(queriesRes.data.total ?? null);
            setLoading(false);
        })();
        return () => { cancelled = true; };
    }, [courseId, instructorId, selectedTimeRange, analyticsClient, queryClient]);

    const courseDistribution = queryDistribution.length > 0
        ? queryDistribution.map((d, i) => ({ name: d.courseName, value: d.count, color: CHART_COLORS[i % CHART_COLORS.length] }))
        : [{ name: course.name, value: totalChatbotQueries || 1, color: CHART_COLORS[0] }];

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
                    <p className="text-muted-foreground">Course engagement and chatbot usage insights for {course.name}</p>
                </div>
                <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                    <SelectTrigger className="w-40"><SelectValue placeholder="Time range" /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="7d">Last 7 days</SelectItem>
                        <SelectItem value="30d">Last 30 days</SelectItem>
                        <SelectItem value="90d">Last 90 days</SelectItem>
                        <SelectItem value="1y">Last year</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div>
                <h2 className="text-lg font-semibold mb-3">Platform Engagement</h2>
                <p className="text-sm text-muted-foreground mb-4">Key metrics for course engagement and chatbot usage in the selected time range.</p>
                <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
                    <StatCard value={loading ? "—" : enrolledCount.toLocaleString()} label="Enrolled Users" icon={Users} />
                    <StatCard value={loading ? "—" : totalChatbotQueries.toLocaleString()} label="Chatbot Queries" icon={MessageSquare} />
                    <StatCard value={loading ? "—" : (overviewSummary?.averageSatisfaction ? `${overviewSummary.averageSatisfaction} / 5.0` : "— / 5.0")} label="Avg. Satisfaction" icon={TrendingUp} />
                    <StatCard value={loading ? "—" : `${engagementScore}%`} label="Engagement Rate" icon={Activity} />
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between gap-2">
                        <div>
                            <CardTitle className="flex items-center gap-2"><HelpCircle className="h-5 w-5" /> Frequently Asked Questions</CardTitle>
                            <CardDescription>Top questions students asked in this course (by count)</CardDescription>
                        </div>
                        <Button variant="outline" size="sm" onClick={() => navigate(`/courses/${courseId}/questions`)}>See All</Button>
                    </CardHeader>
                    <CardContent>
                        {loading ? <p className="text-sm">Loading…</p> : topQuestions.length === 0 ? <p className="text-sm">No questions recorded yet.</p> : (
                            <ul className="space-y-3">
                                {topQuestions.map((item, i) => (
                                    <li key={i} className="border-b pb-2 last:border-0"><div className="flex justify-between gap-4"><span className="text-sm font-medium">{item.queryText}</span><span className="text-sm text-muted-foreground">{item.count}×</span></div></li>
                                ))}
                            </ul>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Top Keywords</CardTitle>
                        <CardDescription>Most common keywords in student questions</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {topKeywords.length === 0 ? <p className="text-sm">No keywords recorded yet.</p> : (
                            <ul className="space-y-3">
                                {topKeywords.map((item, i) => (
                                    <li key={i} className="flex justify-between border-b pb-2 last:border-0"><span className="text-sm">{item.keyword}</span><span className="text-sm font-medium text-muted-foreground">{item.count}×</span></li>
                                ))}
                            </ul>
                        )}
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Chatbot Usage Trend</CardTitle>
                    <CardDescription>Daily chatbot queries and unique users over time</CardDescription>
                </CardHeader>
                <CardContent>
                    <UsageTrendChart data={usageTrend} />
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Chatbot Usage by Course</CardTitle>
                        <CardDescription>Total queries per course</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {/* Now using the imported component */}
                        <CourseBarChart data={courseUsageData} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Query Distribution</CardTitle>
                        <CardDescription>Percentage breakdown by course</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={courseDistribution} cx="50%" cy="50%" outerRadius={100} dataKey="value">
                                    {courseDistribution.map((entry, index) => <Cell key={index} fill={entry.color} />)}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Course Engagement Details</CardTitle>
                    <CardDescription>Detailed metrics for each course</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                            <tr className="border-b bg-muted/30">
                                <th className="p-4 text-left font-semibold">Course</th>
                                <th className="p-4 text-center font-semibold">Total Enrolled</th>
                                <th className="p-4 text-center font-semibold">Engagement Rate</th>
                                <th className="p-4 text-center font-semibold">Chatbot Queries</th>
                                <th className="p-4 text-right font-semibold">Satisfaction</th>
                            </tr>
                            </thead>
                            <tbody>
                            {courseUsageData.map((c) => (
                                <tr key={c.courseId} className="border-b hover:bg-muted/50 transition-colors">
                                    <td className="p-4"><div className="font-bold text-primary">{c.courseCode}</div><div className="text-xs text-muted-foreground">{c.courseName}</div></td>
                                    <td className="p-4 text-center font-medium">{enrolledCount}</td>
                                    <td className="p-4 text-center"><span className="bg-primary/10 text-primary px-2 py-1 rounded-full font-bold">{engagementScore}%</span></td>
                                    <td className="p-4 text-center">{totalChatbotQueries.toLocaleString()}</td>
                                    <td className="p-4 text-right font-bold">★ {overviewSummary?.averageSatisfaction || "—"}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}