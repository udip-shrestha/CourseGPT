import { LayoutDashboard } from "lucide-react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./ui/card";

interface CourseAnalyticsPageProps {
    course: { name: string };
}

export function CourseAnalyticsPage({ course }: CourseAnalyticsPageProps) {
    return (
        <div className="space-y-6">
            <Card className="border-2 border-dashed border-muted">
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-primary/10 p-2">
                            <LayoutDashboard className="h-8 w-8 text-primary" />
                        </div>
                        <div>
                            <CardTitle className="text-xl">Analytics</CardTitle>
                            <CardDescription>
                                Insights and metrics for {course.name}
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                    <p className="text-2xl font-semibold text-foreground">
                        New feature coming soon
                    </p>
                    <p className="mt-2 text-muted-foreground max-w-md">
                        We're building analytics and reporting for your course. Check back later for charts, engagement metrics, and more.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
