import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

// Renamed component for clarity
export function RegisterPage() {
    const navigate = useNavigate();
    const [name, setName] = useState("");
    const [title, setTitle] = useState(""); // Added Title
    const [university, setUniversity] = useState(""); // Added University
    const [email, setEmail] = useState("");
    // Removed password states

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- Basic Validation ---
        // Updated validation to include new fields
        if (!name || !title || !university || !email ) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }
        // Add more specific validation (e.g., email format) if needed
        // --- End Validation ---

        // --- Updated data object to match backend ---
        const instructorData = {
            name: name,
            title: title,
            university: university,
            email: email,
        };
        // ---------------------------------------------

        console.log("Submitting Instructor Registration:", instructorData);

        // --- ACTUAL API CALL ---
        try {
            // Assuming your backend runs on port 8000 and has an endpoint like /instructors/
            const response = await fetch('http://localhost:8000/instructors?', { // Adjust endpoint if needed
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(instructorData), // Send the correct data
            });

            if (!response.ok) {
                // Try to get error detail from backend response
                let errorDetail = 'Registration failed. Please try again.';
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                } catch (jsonError) {
                    // If response is not JSON, use default error
                    console.error("Could not parse error response:", jsonError);
                }
                throw new Error(errorDetail);
            }

            const result = await response.json(); // Get the response (e.g., {"instructor_id": "..."})
            console.log('Instructor registration successful:', result);

            // Navigate to login or maybe the new instructor's profile?
            navigate('/login'); // Redirect to login page after successful registration

        } catch (err: any) {
            console.error("Instructor registration failed:", err);
            setError(err.message || "An unexpected error occurred during registration.");
        } finally {
            setIsLoading(false);
        }
        // --- End of API call section ---
    };

    return (
        // Centering container
        <div className="w-full flex items-center justify-center p-4">
            {/* Responsive Card */}
            <Card className="w-full max-w-md shadow-md"> {/* Consistent width */}
                <CardHeader>
                    {/* Updated Title */}
                    <CardTitle>Register as Instructor</CardTitle>
                    <CardDescription>Enter your professional details.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        {/* Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="name">Full Name</Label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="e.g., Dr. Ada Lovelace"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>

                        {/* --- ADDED Title Field --- */}
                        <div className="grid gap-2">
                            <Label htmlFor="title">Title</Label>
                            <Input
                                id="title"
                                type="text"
                                placeholder="e.g., Associate Professor"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                required
                            />
                        </div>
                        {/* ------------------------- */}

                        {/* --- ADDED University Field --- */}
                        <div className="grid gap-2">
                            <Label htmlFor="university">University</Label>
                            <Input
                                id="university"
                                type="text"
                                placeholder="e.g., Tech University"
                                value={university}
                                onChange={(e) => setUniversity(e.target.value)}
                                required
                            />
                        </div>
                        {/* ---------------------------- */}

                        {/* Email */}
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="ada@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        {/* REMOVED Password Fields */}

                        {/* Error Message */}
                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {/* Submit Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Registering..." : "Register Instructor Profile"}
                        </Button>

                        {/* Link back to Login */}
                        <Button
                            type="button"
                            variant="link"
                            className="w-full text-sm"
                            onClick={() => navigate('/login')} // Navigate back to login
                        >
                            Already registered? Sign In
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}

