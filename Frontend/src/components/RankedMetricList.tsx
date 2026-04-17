interface RankedMetricItem {
    label: string;
    value: number;
    helper?: string;
}

interface RankedMetricListProps {
    items: RankedMetricItem[];
    valueLabel: string;
    emptyMessage?: string;
    accentClassName?: string;
    description?: string;
}

export function RankedMetricList({
    items,
    valueLabel,
    emptyMessage = "No data available.",
    accentClassName = "bg-primary",
    description,
}: RankedMetricListProps) {
    if (!items || items.length === 0) {
        return (
            <div className="flex h-[220px] items-center justify-center text-sm italic text-muted-foreground">
                {emptyMessage}
            </div>
        );
    }

    const maxValue = Math.max(...items.map((item) => item.value), 1);
    const totalValue = items.reduce((sum, item) => sum + item.value, 0);

    return (
        <div className="space-y-4">
            {description ? (
                <div className="rounded-2xl border bg-slate-50/70 px-4 py-3 text-sm text-muted-foreground dark:bg-slate-900/50">
                    {description}
                </div>
            ) : null}
            {items.map((item, index) => {
                const width = `${Math.max((item.value / maxValue) * 100, 8)}%`;
                const share = totalValue > 0 ? Math.round((item.value / totalValue) * 100) : 0;

                return (
                    <div key={`${item.label}-${index}`} className="space-y-3 rounded-2xl border p-4">
                        <div className="flex items-center justify-between gap-4">
                            <div className="min-w-0">
                                <div className="flex items-center gap-3">
                                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border bg-background text-sm font-semibold text-muted-foreground">
                                        {index + 1}
                                    </span>
                                    <div className="min-w-0">
                                        <p className="truncate font-medium">{item.label}</p>
                                        {item.helper ? (
                                            <p className="text-xs text-muted-foreground">{item.helper}</p>
                                        ) : null}
                                    </div>
                                </div>
                            </div>
                            <div className="shrink-0 text-right">
                                <p className="text-lg font-bold">{item.value}</p>
                                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                                    {valueLabel}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center justify-between gap-4 text-xs text-muted-foreground">
                            <span>Relative size in this ranking</span>
                            <span className="font-medium">{share}% of shown total</span>
                        </div>

                        <div className="space-y-2">
                            <div className="h-2.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                                <div
                                    className={`h-full rounded-full ${accentClassName}`}
                                    style={{ width }}
                                />
                            </div>
                            <div className="flex justify-between text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                                <span>Lower</span>
                                <span>Higher</span>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
