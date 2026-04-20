import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from "recharts";
import { useState } from "react";

interface CourseBarChartProps {
    data: any[];
    xKey?: string;
    yKey?: string;
}

export function CourseBarChart({ data, xKey = "courseName", yKey = "chatbotQueries" }: CourseBarChartProps) {
    const [activeIndex, setActiveIndex] = useState<number | null>(null);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart
                data={data}
                onMouseMove={(state) => {
                    // Force type to number to satisfy TypeScript
                    if (state && state.activeTooltipIndex !== undefined) {
                        setActiveIndex(state.activeTooltipIndex as number);
                    } else {
                        setActiveIndex(null);
                    }
                }}
                onMouseLeave={() => setActiveIndex(null)}
            >
                <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                />
                <XAxis
                    dataKey={xKey}
                    stroke="#008000"
                    tick={{ fill: "#008000", fontSize: 12 }}
                />
                <YAxis
                    stroke="#008000"
                    tick={{ fill: "#008000", fontSize: 12 }}
                />
                <Tooltip
                    cursor={{ fill: 'transparent' }}
                    contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "none",
                        borderRadius: "8px",
                        color: "#fff",
                        fontWeight: "bold",
                        boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)"
                    }}
                    itemStyle={{ color: "#ef4444" }}
                />
                <Bar
                    dataKey={yKey}
                    name="Queries"
                    radius={[4, 4, 0, 0]}
                >
                    {data.map((_entry, index) => (
                        <Cell
                            key={`cell-${index}`}
                            fill={index === activeIndex ? "#ef4444" : "#3b82f6"}
                            className="transition-all duration-200 cursor-pointer"
                        />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}