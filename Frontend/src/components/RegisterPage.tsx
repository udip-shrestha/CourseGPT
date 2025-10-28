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
    const [title, setTitle] = useState("");
    const [university, setUniversity] = useState("");
    const [email, setEmail] = useState("");

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // Basic Validation
        if (!name || !title || !university || !email ) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }

        // --- CONSTRUCT URL WITH QUERY PARAMETERS ---
        const params = new URLSearchParams();
        params.append('name', name);
        params.append('title', title);
        params.append('university', university);
        params.append('email', email);

        const url = `http://localhost:8000/instructors?${params.toString()}`;
        console.log("Submitting Instructor Registration via URL:", url);
        // --- END URL CONSTRUCTION ---

        // --- API CALL (Sending data via Query Params) ---
        try {
            const response = await fetch(url, { // Use the constructed URL
                method: 'POST',
                headers: {
                    'accept': 'application/json' // Often needed for FastAPI
                    // No 'Content-Type' or 'body' needed for query params
                },
                // No body property needed here
            });

            if (!response.ok) {
                let errorDetail = `Registration failed with status: ${response.status}. Please try again.`;
                try {
                    // Try to parse error detail even if status indicates failure
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                    if (Array.isArray(errorData.detail)) { // Handle FastAPI validation errors
                        errorDetail = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join(', ');
                    }
                } catch (jsonError) {
                    console.error("Could not parse error response:", jsonError);
                    errorDetail = await response.text() || errorDetail;
                }
                console.error("Backend Error Detail:", errorDetail);
                throw new Error(errorDetail);
            }

            // Status 201 Created is typical for successful POST
            if (response.status === 201) {
                const result = await response.json();
                console.log('Instructor registration successful:', result);
                navigate('/login');
            } else {
                // Handle unexpected successful status codes if needed
                const responseText = await response.text();
                console.warn("Unexpected success status:", response.status, responseText);
                // Still navigate, or show a warning?
                navigate('/login');
            }


        } catch (err: any) {
            console.error("Instructor registration failed (fetch error):", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server. Please ensure it's running and check CORS settings.");
            } else {
                setError(err.message || "An unexpected error occurred during registration.");
            }
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
                        {/* Title Field */}
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
                        {/* University Field */}
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

