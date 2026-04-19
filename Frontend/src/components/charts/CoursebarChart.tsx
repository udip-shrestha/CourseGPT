import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

interface CourseBarChartProps {
    data: any[]; // Changed to any[] to allow flexible topic/query data
    xKey?: string;
    yKey?: string;
}

export function CourseBarChart({ data, xKey = "courseName", yKey = "chatbotQueries" }: CourseBarChartProps) {
    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
                <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                />
                <XAxis
                    dataKey={xKey} // Use the dynamic key
                    stroke="#008000"
                    tick={{ fill: "#008000" }}
                />
                <YAxis
                    stroke="#008000"
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
                    dataKey={yKey} // Use the dynamic key
                    fill="#3b82f6"
                    name="Queries"
                    radius={[4, 4, 0, 0]}
                />
            </BarChart>
        </ResponsiveContainer>
    );
}