import { useState, useEffect, useMemo } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./ui/card.tsx";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select.tsx";
import { Button } from "./ui/button.tsx";
import { Users, MessageSquare, TrendingUp, Activity, HelpCircle } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { useApiClient } from "../clients/ApiClientContext.tsx";
import type {
    OverviewSummary,
    UsageTrendPoint,
    QueryDistributionItem,
    TopQuestionsItem,
    TopKeywordsItem
} from "../clients/AnalyticsClient";
import { StatCard } from "./StatCard.tsx";
import { CourseBarChart } from "./charts/CoursebarChart.tsx";
import { UsageTrendChart } from "./charts/UsageTrendChart.tsx";
import { QueryDistributionPieChart } from "./charts/QueryDistributionPieChart.tsx";

const CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

// Filler words to filter out of the Top Keywords display
const STOPWORDS = new Set([
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
    "what", "who", "where", "when", "why", "how", "to", "of", "in",
    "for", "on", "with", "at", "by", "from", "up", "about", "into",
    "over", "after", "your", "mine", "my", "me", "you", "they", "them",
    "this", "that", "these", "those", "it", "its", "it's"
]);

interface AdminAnalyticsPageProps {
    course?: { name: string; id?: string; instructor_id?: string };
}

export function AdminAnalyticsPage({ course: _course }: AdminAnalyticsPageProps) {
    const [loading, setLoading] = useState(true);
    const [overviewSummary, setOverviewSummary] = useState<OverviewSummary | null>(null);
    const [usageTrend, setUsageTrend] = useState<UsageTrendPoint[]>([]);
    const [topQuestions, setTopQuestions] = useState<TopQuestionsItem[]>([]);
    const [queryDistribution, setQueryDistribution] = useState<QueryDistributionItem[]>([]);
    const [topKeywords, setTopKeywords] = useState<TopKeywordsItem[]>([]);
    const [totalCount, setTotalCount] = useState<number | null>(null);
    const [enrolledCount, setEnrolledCount] = useState<number>(0);
    const [error, setError] = useState<string | null>(null);
    const [selectedTimeRange, setSelectedTimeRange] = useState("7d");


return (
    <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Admin Analytics Dashboard</h1>
                    <h1 className="text-muted-foreground">Coming Soon...</h1>
                </div>
            </div>
            </div>
)}
