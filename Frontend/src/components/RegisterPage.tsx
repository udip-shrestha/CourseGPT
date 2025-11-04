import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
// --- 1. Import the ApiClient hook ---
import { useApiClient } from "../ApiClientContext";

// Renamed component for clarity
export function RegisterPage() {
    const navigate = useNavigate();
    // --- 2. Initialize the ApiClient ---
    const apiClient = useApiClient();

    // --- 3. Add state for all required fields ---
    const [name, setName] = useState("");
    const [title, setTitle] = useState("");
    const [university, setUniversity] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    // --- End state ---

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // --- 4. Replace the entire handleSubmit function ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- Basic Validation ---
        if (!name || !title || !university || !email || !password || !confirmPassword) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            setIsLoading(false);
            return;
        }
        // --- End Validation ---

        console.log("Submitting new instructor registration...");

        // --- ACTUAL API CALL using ApiClient ---
        try {
            // ApiClient.register handles the form-urlencoded part
            const { data, errorMessage } = await apiClient.register(
                name,
                title,
                university,
                email,
                password
            );

            if (errorMessage) {
                // If the backend sends an error, display it
                throw new Error(errorMessage);
            }

            // ApiClient.register automatically sets the token and instructor ID
            console.log('Instructor registration successful:', data.instructor_id);

            // Navigate to login after successful registration
            navigate('/login');

        } catch (err: any) {
            console.error("Instructor registration failed:", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server. Please ensure it's running.");
            } else {
                setError(err.message || "An unexpected error occurred.");
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
            <Card className="w-full max-w-md shadow-md">
                <CardHeader>
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

                        {/* --- 5. Add Password and Confirm Password fields --- */}
                        <div className="grid gap-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="********"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <Input
                                id="confirmPassword"
                                type="password"
                                placeholder="********"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>
                        {/* --- End of added fields --- */}

                        {/* Error Message */}
                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {/* Submit Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Registering..." : "Create Account"}
                        </Button>

                        {/* Link back to Login */}
                        <Button
                            type="button"
                            variant="link"
                            className="w-full text-sm"
                            onClick={() => navigate('/login')}
                        >
                            Already registered? Sign In
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}

