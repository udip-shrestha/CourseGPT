import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "./ui/card";

interface StatCardProps {
    value: string | number;
    label: string;
    icon: LucideIcon;
    className?: string;
}

export function StatCard({ value, label, icon: Icon, className }: StatCardProps) {
    return (
        <Card className={className}>
            <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-primary/10 p-2">
                        <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                        <p className="text-2xl font-bold">{value}</p>
                        <p className="text-sm text-muted-foreground">{label}</p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
