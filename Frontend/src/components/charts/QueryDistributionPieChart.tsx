// import {
//     PieChart,
//     Pie,
//     Cell,
//     Tooltip,
//     ResponsiveContainer,
//     Legend
// } from "recharts";
//
// interface PieData {
//     name: string;
//     value: number;
//     color: string;
// }
//
// interface QueryDistributionPieChartProps {
//     data: PieData[];
// }
//
// export function QueryDistributionPieChart({ data }: QueryDistributionPieChartProps) {
//     return (
//         <ResponsiveContainer width="100%" height={300}>
//             <PieChart>
//                 <Pie
//                     data={data}
//                     cx="50%"
//                     cy="50%"
//                     innerRadius={60} // Donut style is often cleaner
//                     outerRadius={100}
//                     paddingAngle={5}
//                     dataKey="value"
//                 >
//                     {data.map((entry, index) => (
//                         <Cell key={`cell-${index}`} fill={entry.color} />
//                     ))}
//                 </Pie>
//                 <Tooltip
//                     contentStyle={{
//                         borderRadius: "8px",
//                         border: "1px solid hsl(var(--border))",
//                         backgroundColor: "hsl(var(--card))"
//                     }}
//                 />
//                 <Legend verticalAlign="bottom" height={36}/>
//             </PieChart>
//         </ResponsiveContainer>
//     );
// }