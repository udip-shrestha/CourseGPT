import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
    BarChart3,
    Users,
    MessageSquare,
    TrendingUp,
    Hash,
    ChevronRight,
    Activity,
    Award,
    Loader2
} from 'lucide-react';
import { useApiClient } from "../clients/ApiClientContext";



interface OverviewData {
    total_queries: number;
    active_students: number;
    avg_queries_per_student: number;
    growth?: string;
}

interface QuestionData {
    text: string;
    count: number;
}

interface KeywordData {
    word: string;
    weight: number;
}

interface EngagementData {
    total_students: number;
    active_pct: number;
    discord_usage: number;
    web_usage: number;
}

const CourseAnalyticsPage = () => {
    const { courseId } = useParams<{ courseId: string }>();
    const { courseClient } = useApiClient();

    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState(7);

    // Explicit types for state to prevent 'never' errors
    const [overview, setOverview] = useState<OverviewData | null>(null);
    const [topQuestions, setTopQuestions] = useState<QuestionData[]>([]);
    const [topKeywords, setTopKeywords] = useState<KeywordData[]>([]);
    const [engagement, setEngagement] = useState<EngagementData | null>(null);

    const fetchAnalytics = useCallback(async () => {
        if (!courseId) return;
        setLoading(true);

        try {
            // Promise.all to fetch all analytics endpoints concurrently
            const [ovRes, qRes, kRes, eRes] = await Promise.all([
                courseClient.getCourseOverview?.(courseId, timeRange) || Promise.resolve({ data: null }),
                courseClient.getTopQuestions?.(courseId) || Promise.resolve({ data: [] }),
                courseClient.getTopKeywords?.(courseId) || Promise.resolve({ data: [] }),
                courseClient.getEngagementMetrics?.(courseId) || Promise.resolve({ data: null })
            ]);

            setOverview(ovRes.data || {
                total_queries: 0,
                active_students: 0,
                avg_queries_per_student: 0,
                growth: "0%"
            });
            setTopQuestions(qRes.data || []);
            setTopKeywords(kRes.data || []);
            setEngagement(eRes.data || {
                total_students: 0,
                active_pct: 0,
                discord_usage: 0,
                web_usage: 0
            });
        } catch (error) {
            console.error("Analytics fetch failed:", error);
        } finally {
            setLoading(false);
        }
    }, [courseId, timeRange, courseClient]);

    useEffect(() => {
        fetchAnalytics();
    }, [fetchAnalytics]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                <Loader2 className="h-8 w-8 animate-spin mb-2 text-blue-600" />
                <p className="text-sm font-medium">Analyzing course data...</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header & Filter Controls */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-xl font-bold text-slate-900">Analytics Dashboard</h2>
                    <p className="text-slate-500 text-xs font-medium">Insights for the last {timeRange} days</p>
                </div>

                <div className="flex items-center bg-slate-100 rounded-lg p-1 w-fit shadow-inner">
                    {[7, 30, 90].map((days) => (
                        <button
                            key={days}
                            onClick={() => setTimeRange(days)}
                            className={`px-4 py-1.5 text-xs font-bold rounded-md transition-all ${
                                timeRange === days
                                    ? 'bg-white text-blue-600 shadow-sm'
                                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                            }`}
                        >
                            {days} Days
                        </button>
                    ))}
                </div>
            </div>

            {/* Primary KPI Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Total Queries"
                    value={overview?.total_queries ?? 0}
                    icon={<MessageSquare className="w-4 h-4 text-blue-600" />}
                    trend={overview?.growth}
                />
                <StatCard
                    title="Active Students"
                    value={overview?.active_students ?? 0}
                    icon={<Users className="w-4 h-4 text-indigo-600" />}
                />
                <StatCard
                    title="Avg. Daily Queries"
                    value={overview?.avg_queries_per_student ?? 0}
                    icon={<TrendingUp className="w-4 h-4 text-emerald-600" />}
                />
                <StatCard
                    title="Active Student %"
                    value={`${engagement?.active_pct ?? 0}%`}
                    icon={<Activity className="w-4 h-4 text-orange-600" />}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Most Frequent Questions - Main View */}
                <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-blue-500" />
                        <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wide">Top Student Questions</h3>
                    </div>
                    <div className="divide-y divide-slate-100">
                        {topQuestions.length > 0 ? topQuestions.map((q, i) => (
                            <div key={i} className="p-4 flex items-center justify-between hover:bg-slate-50/80 transition-colors group">
                                <div className="flex items-center gap-4">
                                    <span className="text-xs font-black text-slate-300 group-hover:text-blue-200 transition-colors w-4">{i + 1}</span>
                                    <p className="text-sm text-slate-700 font-semibold">{q.text}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="flex flex-col items-end">
                                        <span className="text-xs font-black text-slate-900">{q.count}</span>
                                        <span className="text-[10px] font-bold text-slate-400 uppercase">Hits</span>
                                    </div>
                                    <ChevronRight className="w-4 h-4 text-slate-200 group-hover:text-slate-400" />
                                </div>
                            </div>
                        )) : (
                            <div className="p-12 text-center">
                                <p className="text-sm text-slate-400 font-medium italic">No frequent questions found for this period.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar: Keywords & Engagement Breakdown */}
                <div className="space-y-6">
                    {/* Keywords Breakdown */}
                    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
                        <h3 className="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-5">
                            <Hash className="w-4 h-4 text-indigo-500" />
                            Trending Keywords
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {topKeywords.length > 0 ? topKeywords.map((k, i) => (
                                <span
                                    key={i}
                                    className="px-2.5 py-1.5 bg-indigo-50/50 border border-indigo-100 text-indigo-700 rounded-lg text-xs font-bold hover:bg-indigo-100 transition-colors cursor-default"
                                >
                  {k.word} <span className="opacity-40 ml-1">({k.weight})</span>
                </span>
                            ) ) : (
                                <p className="text-xs text-slate-400 italic">No keywords extracted yet.</p>
                            )}
                        </div>
                    </div>

                    {/* Integration Usage */}
                    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
                        <h3 className="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-6">
                            <Award className="w-4 h-4 text-orange-500" />
                            Platform Distribution
                        </h3>
                        <div className="space-y-5">
                            <ProgressBar
                                label="Web Interface"
                                value={engagement?.web_usage ?? 0}
                                color="bg-blue-600"
                            />
                            <ProgressBar
                                label="Discord Integration"
                                value={engagement?.discord_usage ?? 0}
                                color="bg-indigo-600"
                            />
                        </div>

                        <div className="mt-8 pt-5 border-t border-slate-100 flex items-center justify-between">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Total Enrolled</span>
                            <span className="text-sm font-black text-slate-900">{engagement?.total_students ?? 0}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- Sub-components for cleaner structure ---

const StatCard = ({ title, value, icon, trend }: { title: string, value: string | number, icon: React.ReactNode, trend?: string }) => (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 transition-all">
        <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-slate-50 rounded-lg shadow-inner">{icon}</div>
            {trend && (
                <div className="flex items-center text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded text-[10px] font-black">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {trend}
                </div>
            )}
        </div>
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">{title}</p>
        <p className="text-2xl font-black text-slate-900 tabular-nums">{value}</p>
    </div>
);

const ProgressBar = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-2">
        <div className="flex justify-between text-[10px] font-black uppercase tracking-wider">
            <span className="text-slate-500">{label}</span>
            <span className="text-slate-900">{value}%</span>
        </div>
        <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden shadow-inner">
            <div
                className={`h-full ${color} rounded-full transition-all duration-700 ease-out`}
                style={{ width: `${value}%` }}
            />
        </div>
    </div>
);

export default CourseAnalyticsPage;