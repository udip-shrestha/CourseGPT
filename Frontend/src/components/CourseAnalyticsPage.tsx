import { useState } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./ui/card";
import { StatCard } from "./StatCard";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select";
import { Users, MessageSquare, TrendingUp, Activity } from "lucide-react";
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

interface CourseAnalyticsPageProps {
    course: { name: string; id?: string };
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

interface ChatbotUsageData {
    date: string;
    queries: number;
    uniqueUsers: number;
}

interface CourseDistributionData {
    name: string;
    value: number;
    color: string;
    [key: string]: string | number;
}

export function CourseAnalyticsPage({ course }: CourseAnalyticsPageProps) {
    const [selectedTimeRange, setSelectedTimeRange] = useState("7d");
    const [selectedCourse, setSelectedCourse] = useState("all");

    // Mock data - Course usage statistics
    const courseUsageData: CourseUsageData[] = [
        {
            courseId: "1",
            courseName: "Introduction to Machine Learning",
            courseCode: "CS 480",
            activeUsers: 72,
            totalUsers: 85,
            chatbotQueries: 1543,
            averageResponseTime: 1.2,
            satisfaction: 4.6,
        },
        {
            courseId: "2",
            courseName: "Advanced Data Science",
            courseCode: "CS 580",
            activeUsers: 58,
            totalUsers: 62,
            chatbotQueries: 987,
            averageResponseTime: 1.5,
            satisfaction: 4.4,
        },
        {
            courseId: "3",
            courseName: "Python Programming",
            courseCode: "CS 101",
            activeUsers: 98,
            totalUsers: 120,
            chatbotQueries: 2341,
            averageResponseTime: 0.9,
            satisfaction: 4.8,
        },
    ];

    // Mock data - Chatbot usage over time
    const chatbotTrendData: ChatbotUsageData[] = [
        { date: "2024-02-03", queries: 234, uniqueUsers: 45 },
        { date: "2024-02-04", queries: 312, uniqueUsers: 52 },
        { date: "2024-02-05", queries: 289, uniqueUsers: 48 },
        { date: "2024-02-06", queries: 401, uniqueUsers: 61 },
        { date: "2024-02-07", queries: 456, uniqueUsers: 68 },
        { date: "2024-02-08", queries: 378, uniqueUsers: 55 },
        { date: "2024-02-09", queries: 423, uniqueUsers: 63 },
    ];

    // Mock data - Course distribution
    const courseDistribution: CourseDistributionData[] = [
        { name: "CS 480", value: 1543, color: "#3b82f6" },
        { name: "CS 580", value: 987, color: "#10b981" },
        { name: "CS 101", value: 2341, color: "#f59e0b" },
    ];

    // Calculate aggregated statistics
    const totalActiveUsers = courseUsageData.reduce(
        (sum, c) => sum + c.activeUsers,
        0
    );
    const totalChatbotQueries = courseUsageData.reduce(
        (sum, c) => sum + c.chatbotQueries,
        0
    );
    const averageSatisfaction = (
        courseUsageData.reduce((sum, c) => sum + c.satisfaction, 0) /
        courseUsageData.length
    ).toFixed(1);
    const totalEnrolledUsers = courseUsageData.reduce(
        (sum, c) => sum + c.totalUsers,
        0
    );

    // Filter data based on selected course
    const filteredCourseData =
        selectedCourse === "all"
            ? courseUsageData
            : courseUsageData.filter((c) => c.courseId === selectedCourse);

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
                    <Select value={selectedCourse} onValueChange={setSelectedCourse}>
                        <SelectTrigger className="w-48">
                            <SelectValue placeholder="Select course" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Courses</SelectItem>
                            {courseUsageData.map((c) => (
                                <SelectItem key={c.courseId} value={c.courseId}>
                                    {c.courseCode}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
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

            {/* Key Metrics */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
                <StatCard value={totalActiveUsers} label="Active Users" icon={Users} />
                <StatCard
                    value={totalChatbotQueries.toLocaleString()}
                    label="Chatbot Queries"
                    icon={MessageSquare}
                />
                <StatCard
                    value={`${averageSatisfaction}/5.0`}
                    label="Avg. Satisfaction"
                    icon={TrendingUp}
                />
                <StatCard
                    value={`${((totalActiveUsers / totalEnrolledUsers) * 100).toFixed(0)}%`}
                    label="Engagement Rate"
                    icon={Activity}
                />
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
                        <LineChart data={chatbotTrendData}>
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
                            <BarChart data={filteredCourseData}>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="hsl(var(--border))"
                                />
                                <XAxis
                                    dataKey="courseCode"
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
                                {filteredCourseData.map((c) => (
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
