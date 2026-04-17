import {
    Bar,
    BarChart,
    CartesianGrid,
    Label,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

interface MetricBarChartData {
    label: string;
    value: number;
}

interface MetricBarChartProps {
    data: MetricBarChartData[];
    valueLabel: string;
    color?: string;
    height?: number;
    xAxisLabel?: string;
}

export function MetricBarChart({
    data,
    valueLabel,
    color = "#2563eb",
    height,
    xAxisLabel,
}: MetricBarChartProps) {
    const chartHeight = height ?? Math.max(180, data.length * 52);

    if (!data || data.length === 0) {
        return (
            <div className="flex h-[220px] items-center justify-center text-sm italic text-muted-foreground">
                No chart data available.
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart data={data} layout="vertical" margin={{ top: 8, left: 20, right: 20, bottom: 18 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} strokeOpacity={0.2} />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12}>
                    {xAxisLabel ? (
                        <Label value={xAxisLabel} position="insideBottom" offset={-8} style={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                    ) : null}
                </XAxis>
                <YAxis
                    dataKey="label"
                    type="category"
                    width={120}
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                />
                <Tooltip
                    formatter={(value: number) => [value, valueLabel]}
                    contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                    }}
                />
                <Bar dataKey="value" fill={color} radius={[0, 6, 6, 0]} name={valueLabel} barSize={28} />
            </BarChart>
        </ResponsiveContainer>
    );
}
