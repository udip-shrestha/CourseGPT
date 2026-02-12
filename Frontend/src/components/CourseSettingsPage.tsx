import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select";
import { useApiClient } from "../clients/ApiClientContext";

interface Course {
    id: string;
    name: string;
    institution: string;
    semester_id: number;
    year: number;
    instructor_id?: string;
    created_at?: string;
}

// Semester mapping (common values: 1=Spring, 2=Summer, 3=Fall, 4=Winter)
const SEMESTER_OPTIONS = [
    { value: 1, label: "Spring" },
    { value: 2, label: "Summer" },
    { value: 3, label: "Fall" },
    { value: 4, label: "Winter" },
];

export function SettingsPage() {
    const navigate = useNavigate();
    const { courseClient } = useApiClient();
    const { courseId } = useParams<{ courseId: string }>();

    // Course data state
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        name: "",
        institution: "",
        semester_id: 3, // Default to Fall
        year: new Date().getFullYear(),
    });
    const [isSaving, setIsSaving] = useState(false);
    const [saveError, setSaveError] = useState<string | null>(null);
    const [saveSuccess, setSaveSuccess] = useState(false);
    
    // Fetch course data on mount
    useEffect(() => {

        if (!courseId) {
            setLoadError("Course ID is required.");
            setIsLoading(false);
            return;
        }

        const fetchCourse = async () => {
            setIsLoading(true);
            setLoadError(null);
            try {
                const { data, errorMessage } = await courseClient.getCourse(
                    courseId,
                );
                const courseData = data as Course | undefined;

                if (errorMessage) {
                    setLoadError(errorMessage);
                    return;
                }

                if (courseData) {
                    setFormData({
                        name: courseData.name || "",
                        institution: courseData.institution || "",
                        semester_id: courseData.semester_id || 3,
                        year: courseData.year || new Date().getFullYear(),
                    });
                }
            } catch (error) {
                console.error("Failed to fetch course:", error);
                setLoadError("Failed to load course data.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchCourse();
    }, [courseId, navigate, courseClient]);

    const handleInputChange = (
        field: keyof typeof formData,
        value: string | number,
    ) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
        setSaveError(null);
        setSaveSuccess(false);
    };

    const handleSaveCourse = async () => {
        if (!courseId) return;

        setIsSaving(true);
        setSaveError(null);
        setSaveSuccess(false);

        try {
            const { errorMessage } = await courseClient.updateCourse(courseId, {
                name: formData.name,
                institution: formData.institution,
                semester_id: formData.semester_id,
                year: formData.year,
            });

            if (errorMessage) {
                setSaveError(errorMessage);
                return;
            }

            setSaveSuccess(true);
            // Refresh course data to get updated values
            const { data } = await courseClient.getCourse(courseId);
            const updatedData = data as Course | undefined;
            if (updatedData) {
                setFormData({
                    name: updatedData.name || "",
                    institution: updatedData.institution || "",
                    semester_id: updatedData.semester_id || 3,
                    year: updatedData.year || new Date().getFullYear(),
                });
            }
            // Clear success message after 3 seconds
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (error) {
            console.error("Failed to update course:", error);
            setSaveError("Failed to update course. Please try again.");
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <Card>
                    <CardContent className="py-10">
                        <p className="text-center text-muted-foreground">
                            Loading course information...
                        </p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (loadError) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <Card>
                    <CardContent className="py-10">
                        <p className="text-center text-destructive">{loadError}</p>
                        <div className="mt-4 text-center">
                            <Button
                                variant="outline"
                                onClick={() => navigate(-1)}
                            >
                                Go Back
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            {/* Course Details Card */}
            <Card>
                <CardHeader>
                    <CardTitle>Course Settings</CardTitle>
                    <CardDescription>
                        Update your course information. Changes will be saved to your
                        course profile.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* <div className="space-y-2">
                        <Label htmlFor="course-id">Course ID</Label>
                        <Input
                            id="course-id"
                            value={courseId || "Unknown"}
                            readOnly
                            className="bg-muted"
                        />
                    </div> */}

                    <div className="space-y-2">
                        <Label htmlFor="name">Course Name</Label>
                        <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) =>
                                handleInputChange("name", e.target.value)
                            }
                            placeholder="Enter course name"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="institution">Institution</Label>
                        <Input
                            id="institution"
                            value={formData.institution}
                            onChange={(e) =>
                                handleInputChange("institution", e.target.value)
                            }
                            placeholder="Enter institution name"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="semester">Semester</Label>
                        <Select
                            value={formData.semester_id.toString()}
                            onValueChange={(value) =>
                                handleInputChange("semester_id", parseInt(value))
                            }
                        >
                            <SelectTrigger id="semester">
                                <SelectValue placeholder="Select semester" />
                            </SelectTrigger>
                            <SelectContent>
                                {SEMESTER_OPTIONS.map((semester) => (
                                    <SelectItem
                                        key={semester.value}
                                        value={semester.value.toString()}
                                    >
                                        {semester.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="year">Year</Label>
                        <Input
                            id="year"
                            type="number"
                            value={formData.year}
                            onChange={(e) =>
                                handleInputChange(
                                    "year",
                                    parseInt(e.target.value) || new Date().getFullYear(),
                                )
                            }
                            placeholder="Enter academic year"
                            min="2000"
                            max="2100"
                        />
                    </div>

                    {saveError && (
                        <p className="text-sm text-destructive">{saveError}</p>
                    )}
                    {saveSuccess && (
                        <p className="text-sm text-green-600">
                            Course updated successfully!
                        </p>
                    )}

                    <Button
                        onClick={handleSaveCourse}
                        disabled={isSaving}
                        className="w-full sm:w-auto"
                    >
                        {isSaving ? "Saving..." : "Save Changes"}
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
