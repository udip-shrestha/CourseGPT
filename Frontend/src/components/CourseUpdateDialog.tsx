import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import {
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogClose
} from "./ui/dialog";

import { useApiClient } from "../ApiClientContext";
import type { CourseSummary } from "./InstructorCourses";
import { semesterMap, type SemesterName, semesterIdToName } from "../semester";

interface CourseUpdateDialogProps {
    course: CourseSummary;
    onCourseUpdated: () => void;
    onClose: () => void;
}

const semesterOptions: SemesterName[] = ["Spring", "Summer", "Fall"];

export function CourseUpdateDialog({ course, onCourseUpdated, onClose }: CourseUpdateDialogProps) {
    const apiClient = useApiClient();

    const [name, setName] = useState(course.name);
    const [institution, setInstitution] = useState(course.institution);
    const [semesterName, setSemesterName] = useState<SemesterName>(semesterIdToName(course.semester_id) as SemesterName);
    const [year, setYear] = useState<number | string>(course.year);

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setName(course.name);
        setInstitution(course.institution);
        setSemesterName(semesterIdToName(course.semester_id) as SemesterName);
        setYear(course.year);
    }, [course]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        const semesterId = semesterMap[semesterName];
        const numericYear = Number(year);

        if (isNaN(numericYear) || numericYear < 2000) {
            setError("Year must be valid.");
            setIsLoading(false);
            return;
        }

        const updatedData = {
            name,
            institution,
            semester_id: semesterId,
            year: numericYear,
        };

        try {
            const { errorMessage } = await apiClient.updateCourse(course.id, updatedData);

            if (errorMessage) throw new Error(errorMessage);

            onCourseUpdated();
        } catch (err: any) {
            setError(err.message || "Failed to update.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <DialogContent className="max-w-lg">
            <DialogHeader>
                <DialogTitle>Update Course</DialogTitle>
                <DialogDescription>Modify the fields below and save changes.</DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label>Name</Label>
                    <Input value={name} onChange={(e) => setName(e.target.value)} className="col-span-3" required />
                </div>

                <div className="grid grid-cols-4 items-center gap-4">
                    <Label>Institution</Label>
                    <Input value={institution} onChange={(e) => setInstitution(e.target.value)} className="col-span-3" required />
                </div>

                <div className="grid grid-cols-4 items-center gap-4">
                    <Label>Semester</Label>
                    <Select value={semesterName} onValueChange={(val) => setSemesterName(val as SemesterName)}>
                        <SelectTrigger className="col-span-3">
                            <SelectValue placeholder="Semester" />
                        </SelectTrigger>
                        <SelectContent>
                            {semesterOptions.map((opt) => (
                                <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="grid grid-cols-4 items-center gap-4">
                    <Label>Year</Label>
                    <Input type="number" value={year} onChange={(e) => setYear(e.target.value)} className="col-span-3" min="2000" required />
                </div>

                {error && (
                    <p className="text-sm text-destructive text-center col-span-4">{error}</p>
                )}

                <DialogFooter>
                    <DialogClose asChild>
                        <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>Cancel</Button>
                    </DialogClose>
                    <Button type="submit" disabled={isLoading}>{isLoading ? "Saving..." : "Save Changes"}</Button>
                </DialogFooter>
            </form>
        </DialogContent>
    );
}
