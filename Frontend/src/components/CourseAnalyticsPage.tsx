import { useState, useEffect} from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select";
import { Button } from "./ui/button";
import { Users, MessageSquare, TrendingUp, Activity, HelpCircle } from "lucide-react";
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { useNavigate, useParams } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext";
import type { OverviewSummary, UsageTrendPoint, QueryDistributionItem, TopQuestionsItem, TopKeywordsItem} from "../clients/AnalyticsClient";
import { StatCard } from "./StatCard";

const CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

interface CourseAnalyticsPageProps {
    course: { name: string; id?: string; instructor_id?: string };
}

interface CourseUsageData {
    courseId: string;
    courseName: string;
    courseCode: string;
    activeUsers: number;
    totalUsers: number;
    chatbotQueries: number;
    averageResponseTime: number;
    satisfaction: number;
}

interface CourseDistributionData {
    name: string;
    value: number;
    color: string;
    [key: string]: string | number;
}

const MOCK_TREND: UsageTrendPoint[] = [
    { date: "2024-02-03", queries: 234, uniqueUsers: 45 },
    { date: "2024-02-04", queries: 312, uniqueUsers: 52 },
    { date: "2024-02-05", queries: 289, uniqueUsers: 48 },
    { date: "2024-02-06", queries: 401, uniqueUsers: 61 },
    { date: "2024-02-07", queries: 456, uniqueUsers: 68 },
    { date: "2024-02-08", queries: 378, uniqueUsers: 55 },
    { date: "2024-02-09", queries: 423, uniqueUsers: 63 },
];

export function CourseAnalyticsPage({ course }: CourseAnalyticsPageProps) {
    const [selectedTimeRange, setSelectedTimeRange] = useState("7d");
    const [loading, setLoading] = useState(true);
    const [overviewSummary, setOverviewSummary] = useState<OverviewSummary | null>(null);
    const [usageTrend, setUsageTrend] = useState<UsageTrendPoint[]>(MOCK_TREND);
    const [topQuestions, setTopQuestions] = useState<TopQuestionsItem[]>([]);
    const [queryDistribution, setQueryDistribution] = useState<QueryDistributionItem[]>([]);
    const [topKeywords, setTopKeywords] = useState<TopKeywordsItem[]>([]);
    const [totalCount, setTotalCount] = useState<number | null>(null);

    const { analyticsClient, queryClient } = useApiClient();
    const navigate = useNavigate();
    const { courseId: routeCourseId } = useParams();
    const courseId = course.id ?? routeCourseId ?? "";
    const instructorId = course.instructor_id;

    // Mock data for course table and bar chart (when no API or single-course view)
    const courseUsageData: CourseUsageData[] = [
        {
            courseId: "1",
            courseName: course.name,
            courseCode: course.name.slice(0, 8),
            activeUsers: overviewSummary?.activeUsers ?? 0,
            totalUsers: overviewSummary?.totalEnrolled ?? 0,
            chatbotQueries: overviewSummary?.totalQueries ?? 0,
            averageResponseTime: 0,
            satisfaction: 0,
        },
    ];

    useEffect(() => {
        if (!courseId) {
            setTotalCount(null);
            setLoading(false);
            return;
        }
        let cancelled = false;
        setLoading(true);
        (async () => {
            const [overviewSummaryRes, trendRes, topQuestionsRes, distRes, topKeywordsRes, courseQueriesRes] =
                await Promise.all([
                    analyticsClient.getOverviewSummary(courseId, selectedTimeRange),
                    analyticsClient.getUsageTrend(courseId, selectedTimeRange),
                    analyticsClient.getTopQuestions(courseId, 10, selectedTimeRange),
                    instructorId
                        ? analyticsClient.getQueryDistribution(instructorId, selectedTimeRange)
                        : Promise.resolve({ data: undefined, errorStatus: 404 }),
                    analyticsClient.topKeywords(courseId, 5, selectedTimeRange),
                    queryClient.getCourseQueries(courseId, {
                        limit: 1,
                        offset: 0,
                        orderBy: "asked_at",
                        orderDir: "desc",
                    }),
                ]);
            if (cancelled) return;
            if (overviewSummaryRes.data) setOverviewSummary(overviewSummaryRes.data);
            if (trendRes.data && trendRes.data.length > 0) setUsageTrend(trendRes.data);
            else setUsageTrend([]);
            if (topQuestionsRes.data) setTopQuestions(topQuestionsRes.data);
            else setTopQuestions([]);
            if (distRes.data) setQueryDistribution(distRes.data);
            else setQueryDistribution([]);
            if (topKeywordsRes.data) setTopKeywords(topKeywordsRes.data);
            else setTopKeywords([]);
            if ("errorMessage" in courseQueriesRes && courseQueriesRes.errorMessage) {
                setTotalCount(null);
            } else if (courseQueriesRes.data) {
                setTotalCount(
                    courseQueriesRes.data.total ?? courseQueriesRes.data.queries?.length ?? null
                );
            } else {
                setTotalCount(null);
            }
            setLoading(false);
        })();
    }, [courseId, instructorId, selectedTimeRange, analyticsClient, queryClient]);

    const totalActiveUsers = overviewSummary?.activeUsers ?? courseUsageData[0]?.activeUsers ?? 0;
    const totalChatbotQueries = overviewSummary?.totalQueries ?? courseUsageData[0]?.chatbotQueries ?? 0;
    const averageSatisfaction = "4.6";
    const totalEnrolledUsers = overviewSummary?.totalEnrolled ?? courseUsageData[0]?.totalUsers ?? 0;
    const engagementRate =
        overviewSummary?.engagementRate ?? (totalEnrolledUsers ? Math.round((totalActiveUsers / totalEnrolledUsers) * 100) : 0);

    const courseDistribution: CourseDistributionData[] =
        queryDistribution.length > 0
            ? queryDistribution.map((d, i) => ({
                  name: d.courseName,
                  value: d.count,
                  color: CHART_COLORS[i % CHART_COLORS.length],
              }))
            : [
                  { name: course.name, value: totalChatbotQueries || 1, color: CHART_COLORS[0] },
              ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
                    <p className="text-muted-foreground">
                        Course engagement and chatbot usage insights for{" "}
                        {course.name}
                    </p>
                </div>
                <div className="flex flex-wrap gap-4">
                    <Select
                        value={selectedTimeRange}
                        onValueChange={setSelectedTimeRange}
                    >
                        <SelectTrigger className="w-40">
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

            {/* Platform Engagement */}
            <div>
                <h2 className="text-lg font-semibold mb-3">Platform Engagement</h2>
                <p className="text-sm text-muted-foreground mb-4">
                    Key metrics for course engagement and chatbot usage in the selected time range.
                </p>
                <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
                    <StatCard
                        value={
                            loading
                                ? "—"
                                : overviewSummary?.activeUsers != null
                                ? totalActiveUsers
                                : "N/A"
                        }
                        label="Enrolled Users"
                        icon={Users}
                    />
                    <StatCard
                        value={
                            loading
                                ? "—"
                                : totalCount != null
                                  ? totalCount.toLocaleString()
                                  : overviewSummary?.totalQueries != null
                                    ? totalChatbotQueries.toLocaleString()
                                    : "N/A"
                        }
                        label="Chatbot Queries"
                        icon={MessageSquare}
                    />
                    <StatCard
                        value={overviewSummary ? `-/5.0` : "N/A"}
                        label="Avg. Satisfaction"
                        icon={TrendingUp}
                    />
                    <StatCard
                        value={
                            loading
                                ? "—"
                                : overviewSummary?.engagementRate != null
                                ? `${engagementRate}%`
                                : "N/A"
                        }
                        label="Engagement Rate"
                        icon={Activity}
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Frequently Asked Questions */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between gap-2">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <HelpCircle className="h-5 w-5" />
                                Frequently Asked Questions
                            </CardTitle>
                            <CardDescription>
                                Top questions students asked in this course (by count)
                            </CardDescription>
                        </div>
                        {courseId && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => navigate(`/courses/${courseId}/questions`)}
                            >
                                See All
                            </Button>
                        )}
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <p className="text-muted-foreground text-sm">Loading…</p>
                        ) : topQuestions.length === 0 ? (
                            <p className="text-muted-foreground text-sm">No questions recorded yet.</p>
                        ) : (
                            <ul className="space-y-3">
                                {topQuestions.map((item, i) => (
                                    <li key={i} className="border-b border-border pb-2 last:border-0 space-y-1">
                                        <div className="flex justify-between gap-4">
                                        <span className="text-sm font-medium flex-1 min-w-0">{item.queryText}</span>
                                        <span className="text-sm text-muted-foreground shrink-0">
                                            {item.count} {item.count === 1 ? "time" : "times"}
                                        </span>
                                        </div>
                                        {item.answer && (
                                            <p className="text-sm text-muted-foreground">{item.answer}</p>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </CardContent>
                </Card>

                {/* Top Keywords */}
                <Card>
                    <CardHeader>
                        <CardTitle>Top Keywords</CardTitle>
                        <CardDescription>
                            Most common keywords in student questions
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <p className="text-muted-foreground text-sm">Loading…</p>
                        ) : topKeywords.length === 0 ? (
                            <p className="text-muted-foreground text-sm">No keywords recorded yet.</p>
                        ) : (
                            <ul className="space-y-3">
                                {topKeywords.map((item, i) => (
                                    <li key={i} className="flex justify-between gap-4 border-b border-border pb-2 last:border-0">
                                        <span className="text-sm flex-1 min-w-0">{item.keyword}</span>
                                        <span className="text-sm font-medium text-muted-foreground shrink-0">
                                            {item.count} {item.count === 1 ? "time" : "times"}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Chatbot Usage Trend */}
            <Card>
                <CardHeader>
                    <CardTitle>Chatbot Usage Trend</CardTitle>
                    <CardDescription>
                        Daily chatbot queries and unique users over time
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={usageTrend}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="hsl(var(--border))"
                            />
                            <XAxis
                                dataKey="date"
                                stroke="hsl(var(--muted-foreground))"
                                tick={{ fill: "hsl(var(--muted-foreground))" }}
                            />
                            <YAxis
                                stroke="hsl(var(--muted-foreground))"
                                tick={{ fill: "hsl(var(--muted-foreground))" }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "hsl(var(--card))",
                                    border: "1px solid hsl(var(--border))",
                                    borderRadius: "8px",
                                }}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="queries"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                name="Queries"
                            />
                            <Line
                                type="monotone"
                                dataKey="uniqueUsers"
                                stroke="#10b981"
                                strokeWidth={2}
                                name="Unique Users"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Course-wise Chatbot Usage */}
                <Card>
                    <CardHeader>
                        <CardTitle>Chatbot Usage by Course</CardTitle>
                        <CardDescription>Total queries per course</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={courseUsageData}>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="hsl(var(--border))"
                                />
                                <XAxis
                                    dataKey="courseName"
                                    stroke="#008000" // green color
                                    tick={{ fill: "#008000" }}
                                />
                                <YAxis
                                    stroke="#008000" // green color
                                    tick={{ fill: "#008000" }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "hsl(var(--card))",
                                        border: "1px solid hsl(var(--border))",
                                        borderRadius: "8px",
                                    }}
                                />
                                <Bar
                                    dataKey="chatbotQueries"
                                    fill="#3b82f6"
                                    name="Queries"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Query Distribution */}
                <Card>
                    <CardHeader>
                        <CardTitle>Query Distribution</CardTitle>
                        <CardDescription>
                            Percentage breakdown by course
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={courseDistribution}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }: { name?: string; percent?: number }) =>
                                        `${name ?? ""} ${((percent ?? 0) * 100).toFixed(0)}%`
                                    }
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {courseDistribution.map((entry, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={entry.color}
                                        />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "hsl(var(--card))",
                                        border: "1px solid hsl(var(--border))",
                                        borderRadius: "8px",
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>

            {/* Course Details Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Course Engagement Details</CardTitle>
                    <CardDescription>
                        Detailed metrics for each course
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b">
                                    <th className="p-4 text-left">Course</th>
                                    {/* <th className="p-4 text-left">Active Users</th> */}
                                    <th className="p-4 text-left">Total Enrolled</th>
                                    <th className="p-4 text-left">Engagement Rate</th>
                                    <th className="p-4 text-left">Chatbot Queries</th>
                                    <th className="p-4 text-left">Avg. Response Time</th>
                                    <th className="p-4 text-left">Satisfaction</th>
                                </tr>
                            </thead>
                            <tbody>
                                {courseUsageData.map((c) => (
                                    <tr
                                        key={c.courseId}
                                        className="border-b hover:bg-muted/50"
                                    >
                                        <td className="p-4">
                                            <div>
                                                <div className="font-medium">
                                                    {c.courseCode}
                                                </div>
                                                <div className="text-sm text-muted-foreground">
                                                    {c.courseName}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            {overviewSummary?.activeUsers != null ? c.activeUsers : "N/A"}
                                        </td>
                                        <td className="p-4">
                                            {overviewSummary?.totalEnrolled != null ? c.totalUsers : "N/A"}
                                        </td>
                                        <td className="p-4">
                                            {overviewSummary?.engagementRate != null ? (
                                                <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-1 text-primary">
                                                    {((c.activeUsers / c.totalUsers) * 100).toFixed(0)}%
                                                </span>
                                            ) : (
                                                "N/A"
                                            )}
                                        </td>
                                        <td className="p-4">
                                            {overviewSummary?.totalQueries != null
                                                ? c.chatbotQueries.toLocaleString()
                                                : "N/A"}
                                        </td>
                                        <td className="p-4">
                                            {overviewSummary ? `${c.averageResponseTime}s` : "N/A"}
                                        </td>
                                        <td className="p-4">
                                            {overviewSummary ? (
                                                <span className="inline-flex items-center gap-1">
                                                    ⭐ {c.satisfaction}/5.0
                                                </span>
                                            ) : (
                                                "N/A"
                                            )}
                                        </td>
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
