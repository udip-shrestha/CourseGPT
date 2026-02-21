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

    const { analyticsClient } = useApiClient();
    const courseId = course.id;
    const instructorId = course.instructor_id;

    // Mock data for course table and bar chart (when no API or single-course view)
    const courseUsageData: CourseUsageData[] = [
        {
            courseId: "1",
            courseName: course.name,
            courseCode: course.name.slice(0, 8),
            activeUsers: overviewSummary?.activeUsers ?? 72,
            totalUsers: overviewSummary?.totalEnrolled ?? 85,
            chatbotQueries: overviewSummary?.totalQueries ?? 1543,
            averageResponseTime: 1.2,
            satisfaction: 4.6,
        },
    ];

    useEffect(() => {
        if (!courseId) {
            setLoading(false);
            return;
        }
        let cancelled = false;
        setLoading(true);
        (async () => {
            const [overviewSummaryRes, trendRes, topQuestionsRes, distRes, topKeywordsRes] = await Promise.all([
                analyticsClient.getOverviewSummary(courseId, selectedTimeRange),
                analyticsClient.getUsageTrend(courseId, selectedTimeRange),
                analyticsClient.getTopQuestions(courseId, 10, selectedTimeRange),
                instructorId
                    ? analyticsClient.getQueryDistribution(instructorId, selectedTimeRange)
                    : Promise.resolve({ data: undefined, errorStatus: 404 }),
                analyticsClient.topKeywords(courseId, 10, selectedTimeRange),
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
            setLoading(false);
        })();
    }, [courseId, instructorId, selectedTimeRange, analyticsClient]);

    const totalActiveUsers = overviewSummary?.activeUsers ?? courseUsageData[0]?.activeUsers ?? 0;
    const totalChatbotQueries = overviewSummary?.totalQueries ?? courseUsageData[0]?.chatbotQueries ?? 0;
    const averageSatisfaction = "4.6";
    const totalEnrolledUsers = overviewSummary?.totalEnrolled ?? courseUsageData[0]?.totalUsers ?? 1;
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
                    <StatCard value={loading ? "—" : totalActiveUsers} label="Active Users" icon={Users} />
                    <StatCard
                        value={loading ? "—" : totalChatbotQueries.toLocaleString()}
                        label="Chatbot Queries"
                        icon={MessageSquare}
                    />
                    <StatCard
                        value={`${averageSatisfaction}/5.0`}
                        label="Avg. Satisfaction"
                        icon={TrendingUp}
                    />
                    <StatCard
                        value={loading ? "—" : `${engagementRate}%`}
                        label="Engagement Rate"
                        icon={Activity}
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Frequently Asked Questions */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <HelpCircle className="h-5 w-5" />
                            Frequently Asked Questions
                        </CardTitle>
                        <CardDescription>
                            Top questions students asked in this course (by count)
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <p className="text-muted-foreground text-sm">Loading…</p>
                        ) : topQuestions.length === 0 ? (
                            <p className="text-muted-foreground text-sm">No questions recorded yet.</p>
                        ) : (
                            <ul className="space-y-3">
                                {topQuestions.map((item, i) => (
                                    <li key={i} className="flex justify-between gap-4 border-b border-border pb-2 last:border-0">
                                        <span className="text-sm flex-1 min-w-0">{item.queryText}</span>
                                        <span className="text-sm font-medium text-muted-foreground shrink-0">
                                            {item.count} {item.count === 1 ? "time" : "times"}
                                        </span>
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
                                    <th className="p-4 text-left">Active Users</th>
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
                                        <td className="p-4">{c.activeUsers}</td>
                                        <td className="p-4">{c.totalUsers}</td>
                                        <td className="p-4">
                                            <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-1 text-primary">
                                                {((c.activeUsers / c.totalUsers) * 100).toFixed(0)}%
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {c.chatbotQueries.toLocaleString()}
                                        </td>
                                        <td className="p-4">
                                            {c.averageResponseTime}s
                                        </td>
                                        <td className="p-4">
                                            <span className="inline-flex items-center gap-1">
                                                ⭐ {c.satisfaction}/5.0
                                            </span>
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
