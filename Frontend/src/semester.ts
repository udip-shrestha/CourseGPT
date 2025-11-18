export const semesterMap = {
    Spring: 1,
    Summer: 2,
    Fall: 3,
} as const;

export type SemesterName = keyof typeof semesterMap;

export function semesterIdToName(id: number): SemesterName | "Unknown" {
    return (Object.keys(semesterMap) as SemesterName[]).find(k => semesterMap[k] === id) || "Unknown";
}
