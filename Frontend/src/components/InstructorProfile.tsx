
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Mail } from "lucide-react"; // Only import Mail now

// Define an interface for the expected API response data
interface Instructor {
    id: string;
    name: string;
    title: string;
    university: string;
    email: string;
    created_at: string;
    // Add other fields here if/when your API provides them
}

export function InstructorProfile() {
    // Get the instructorId from the URL path parameter
    const { instructorId } = useParams<{ instructorId: string }>();

    // State for instructor data, loading status, and errors
    const [instructor, setInstructor] = useState<Instructor | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch data when the component mounts or instructorId changes
    useEffect(() => {
        if (!instructorId) {
            setError("Instructor ID not found in URL.");
            setIsLoading(false);
            return;
        }

        const fetchInstructor = async () => {
            setIsLoading(true);
            setError(null);
            try {
                // This uses the correct GET endpoint with the ID from the URL
                const response = await fetch(`http://localhost:8000/instructors/${instructorId}`);
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error(`Instructor with ID ${instructorId} not found.`);
                    }
                    let errorDetail = `Failed to fetch instructor (Status: ${response.status})`;
                    try {
                        const errorData = await response.json();
                        errorDetail = errorData.detail || errorDetail;
                    } catch (_) { /* Ignore if response isn't JSON */ }
                    throw new Error(errorDetail);
                }
                const data: Instructor = await response.json();
                setInstructor(data);
            } catch (err: any) {
                console.error("Failed to fetch instructor:", err);
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setError("Could not connect to the server. Please ensure it's running.");
                } else {
                    setError(err.message || "An unexpected error occurred.");
                }
            } finally {
                setIsLoading(false);
            }
        };

        fetchInstructor();
    }, [instructorId]);

    // --- Render Loading State ---
    if (isLoading) {
        return <div className="text-center p-10">Loading instructor profile...</div>;
    }

    // --- Render Error State ---
    if (error) {
        return <div className="text-center text-destructive p-10">Error: {error}</div>;
    }

    // --- Render Not Found State ---
    if (!instructor) {
        return <div className="text-center p-10">Instructor not found.</div>;
    }

    // --- Render Profile Data ---
    const getInitials = (name: string): string => {
        return name
            .split(' ')
            .map(n => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    }

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <Card>
                <CardContent className="p-8">
                    <div className="flex flex-col md:flex-row gap-6 items-start">
                        {/* Avatar */}
                        <Avatar className="h-32 w-32">
                            <AvatarFallback className="text-4xl">
                                {getInitials(instructor.name)}
                            </AvatarFallback>
                        </Avatar>

                        <div className="flex-1 space-y-4">
                            {/* Basic Info */}
                            <div>
                                <h1 className="text-3xl font-bold">{instructor.name}</h1>
                                <p className="text-xl text-muted-foreground">{instructor.title}</p>
                                <p className="text-lg text-muted-foreground">{instructor.university}</p>
                            </div>

                            {/* Contact Info */}
                            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                    <Mail className="h-4 w-4" />
                                    {instructor.email}
                                </div>
                                {/* Other contact info removed */}
                            </div>
                            {/* Other sections removed */}
                        </div>
                    </div>
                </CardContent>
            </Card>
            {/* Other cards removed */}
        </div>
    );
}