import { useMemo } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
// @ts-ignore
import type { UsageTrendPoint } from "../clients/ApiClientContext";

interface UsageTrendChartProps {
    data: UsageTrendPoint[];
}

export function UsageTrendChart({ data }: UsageTrendChartProps) {
    const queryTrendColor = useMemo(() => {
        if (data.length < 2) return "#3b82f6";
        const first = data[0].queries;
        const last = data[data.length - 1].queries;
        return last >= first ? "#10b981" : "#ef4444";
    }, [data]);

    const userTrendColor = useMemo(() => {
        if (data.length < 2) return "#94a3b8";
        const first = data[0].uniqueUsers;
        const last = data[data.length - 1].uniqueUsers;
        return last >= first ? "#059669" : "#dc2626";
    }, [data]);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.2} />
                <XAxis
                    dataKey="date"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                />
                <YAxis
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                />
                <Tooltip
                    contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px"
                    }}
                />
                <Legend iconType="circle" />
                <Line
                    type="monotone"
                    dataKey="queries"
                    stroke={queryTrendColor}
                    strokeWidth={3}
                    dot={false}
                    name="Total Queries"
                />
                <Line
                    type="monotone"
                    dataKey="uniqueUsers"
                    stroke={userTrendColor}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    name="Unique Users (Students)"
                />
            </LineChart>
        </ResponsiveContainer>
    );
}