import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
// --- 1. IMPORT THE API CLIENT HOOK ---
import { useApiClient } from "../ApiClientContext";

// --- 2. REMOVED the old 'Instructor' interface ---
// (No longer needed)

export function LoginPage() {
    const navigate = useNavigate();
    // --- 3. INITIALIZE THE API CLIENT ---
    const apiClient = useApiClient();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // --- 4. REPLACED 'handleSubmit' with the new version ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- 5. ADDED VALIDATION (Your Suggestion) ---
        // Check if the input looks like an email before sending
        if (!email.includes('@')) {
            setError("Please use your email address to log in, not your name.");
            setIsLoading(false);
            return;
        }
        // --- END OF ADDED VALIDATION ---

        // This now calls the real login endpoint from ApiClient.ts
        try {
            console.log("Login attempt for:", email);

            // This one line handles the API call and password check
            // It correctly sends 'email' as the 'username' field
            const { data, errorMessage } = await apiClient.login(email, password);

            if (errorMessage) {
                throw new Error(errorMessage); // Throw error if login fails
            }

            // On success, the apiClient has stored the token
            // and returned the instructor_id
            const instructorId = data.instructor_id;
            console.log("Login successful for instructor:", instructorId);

            // Navigate to the instructor's profile page
            navigate(`/instructors/${instructorId}/profile`);

        } catch (err: any) {
            console.error("Login failed:", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server. Please ensure it's running and check CORS settings.");
            } else {
                // Display the specific error from the backend (e.g., "Invalid credentials")
                setError(err.message || "Login failed. Please check your email and password.");
            }
        } finally {
            setIsLoading(false);
        }
        // --- End of new handleSubmit ---
    };

    return (
        // The JSX (visual part) remains exactly the same
        <div className="w-full flex items-center justify-center p-4">
            <Card className="w-full max-w-md shadow-md">
                <CardHeader>
                    <CardTitle>Login</CardTitle>
                    <CardDescription>Sign in to your CourseGPT account</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        {/* Email Input */}
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="m@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                aria-invalid={!!error}
                            />
                        </div>
                        {/* Password Input */}
                        <div className="grid gap-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="********"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                aria-invalid={!!error}
                            />
                        </div>

                        {/* Error Message Display */}
                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {/* Sign In Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Signing in..." : "Sign in"}
                        </Button>

                        {/* Register Button */}
                        <Button
                            type="button"
                            variant="outline"
                            className="w-full"
                            onClick={() => navigate('/register')}
                            disabled={isLoading}
                        >
                            Create New Account
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}

