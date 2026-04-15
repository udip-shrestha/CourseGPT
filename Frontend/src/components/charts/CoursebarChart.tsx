import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

interface CourseUsageData {
    courseName: string;
    chatbotQueries: number;
}

interface CourseBarChartProps {
    data: CourseUsageData[];
}

export function CourseBarChart({ data }: CourseBarChartProps) {
    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
                <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
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
    );
}