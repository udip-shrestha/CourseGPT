import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer,
    Legend
} from "recharts";

interface PieData {
    name: string;
    value: number;
    color: string;
    // Add this index signature to satisfy Recharts' ChartDataInput type
    [key: string]: string | number | undefined;
}

interface QueryDistributionPieChartProps {
    data: PieData[];
}

export function QueryDistributionPieChart({ data }: QueryDistributionPieChartProps) {
    // Safety check to prevent Recharts from crashing on empty data
    if (!data || data.length === 0) {
        return (
            <div className="flex h-[300px] items-center justify-center text-muted-foreground italic text-sm">
                No distribution data available.
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={300}>
            <PieChart>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    nameKey="name" // Adding this for better Tooltip/Legend sync
                    animationDuration={1000}
                >
                    {data.map((entry, index) => (
                        <Cell
                            key={`cell-${index}`}
                            fill={entry.color || "#3b82f6"}
                        />
                    ))}
                </Pie>
                <Tooltip
                    contentStyle={{
                        borderRadius: "8px",
                        border: "1px solid hsl(var(--border))",
                        backgroundColor: "hsl(var(--card))",
                        color: "hsl(var(--foreground))"
                    }}
                />
                <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
        </ResponsiveContainer>
    );
}