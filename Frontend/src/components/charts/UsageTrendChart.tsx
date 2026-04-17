import { useMemo } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Label,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
// Corrected import path to reach the interface in AnalyticsClient.ts
import type { UsageTrendPoint } from "../../clients/AnalyticsClient.ts";

interface UsageTrendChartProps {
    data: UsageTrendPoint[];
    height?: number;
}

export function UsageTrendChart({ data, height = 220 }: UsageTrendChartProps) {
    const queryTrendColor = useMemo(() => {
        if (!data || data.length < 2) return "#2563eb";
        const first = data[0].queries;
        const last = data[data.length - 1].queries;
        return last >= first ? "#2563eb" : "#dc2626";
    }, [data]);

    const userTrendColor = useMemo(() => {
        if (!data || data.length < 2) return "#7c3aed";
        const first = data[0].uniqueUsers;
        const last = data[data.length - 1].uniqueUsers;
        return last >= first ? "#7c3aed" : "#c026d3";
    }, [data]);

    // 2. Safe-guard against empty data
    if (!data || data.length === 0) {
        return (
            <div className="flex h-[220px] items-center justify-center text-muted-foreground italic text-sm">
                No trend data available for this time range.
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={height}>
            <LineChart data={data} margin={{ top: 8, right: 24, left: 8, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.2} />
                <XAxis
                    dataKey="date"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickFormatter={(str) => {
                        // Optional: Format "2024-02-03" to "Feb 03" for cleaner look
                        const date = new Date(str);
                        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                    }}
                >
                    <Label value="Date" position="insideBottom" offset={-10} style={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                </XAxis>
                <YAxis
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                >
                    <Label
                        value="Count"
                        angle={-90}
                        position="insideLeft"
                        style={{ fill: "hsl(var(--muted-foreground))", fontSize: 12, textAnchor: "middle" }}
                    />
                </YAxis>
                <Tooltip
                    contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "12px",
                        boxShadow: "0 10px 30px rgba(15, 23, 42, 0.12)",
                    }}
                    labelFormatter={(label) =>
                        new Date(label).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                        })
                    }
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: 16 }} />
                <Line
                    type="monotone"
                    dataKey="queries"
                    stroke={queryTrendColor}
                    strokeWidth={3}
                    dot={{ r: 0 }}
                    activeDot={{ r: 5 }}
                    name="Total Queries"
                    animationDuration={1500}
                />
                <Line
                    type="monotone"
                    dataKey="uniqueUsers"
                    stroke={userTrendColor}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ r: 0 }}
                    activeDot={{ r: 4 }}
                    name="Unique Users (Students)"
                    animationDuration={1500}
                />
            </LineChart>
        </ResponsiveContainer>
    );
}
