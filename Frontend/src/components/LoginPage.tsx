import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

// Define an interface for the Instructor data structure from the API
interface Instructor {
    id: string;
    name: string;
    title: string;
    university: string;
    email: string;
    created_at: string; // Assuming created_at is returned
}

export function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState(""); // Still collect password, even if not checked yet
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- LOGIN USING GET /instructors ---
        try {
            console.log("Simulated login attempt for:", email);

            // 1. Fetch ALL instructors
            const response = await fetch('http://localhost:8000/instructors'); // Adjust URL if needed
            if (!response.ok) {
                throw new Error('Failed to fetch instructor list.');
            }
            const instructors: Instructor[] = await response.json();

            // 2. Find instructor matching the entered email
            const foundInstructor = instructors.find(inst => inst.email.toLowerCase() === email.toLowerCase());

            // 3. Check if instructor was found (and SIMULATE password check)
            if (foundInstructor) {
                // In a real app, I  would verify the password here!
                // For now, I am assuming success if the email exists.
                console.log("Simulated login successful for instructor:", foundInstructor.id);

                // 4. Navigate to the instructor's profile page
                navigate(`/instructors/${foundInstructor.id}/profile`);
                //navigate(`/instructors/${foundInstructor.id}/courses`);

            } else {
                // Instructor email not found
                throw new Error("Login failed. Email not found or password incorrect."); // Generic error
            }

        } catch (err: any) {
            console.error("Login simulation failed:", err);
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                setError("Could not connect to the server. Please ensure it's running and check CORS settings.");
            } else {
                setError(err.message || "Login failed. Please check your email and password.");
            }
        } finally {
            setIsLoading(false);
        }
        // --- End of LOGIN ---
    };

    return (
        // Centering container
        <div className="w-full flex items-center justify-center p-4">
            {/* Responsive Card */}
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
                        {/* Optional: Forgot Password Link */}
                        {/* <Button type="button" variant="link" className="w-full text-sm mt-2">
                            Forgot password?
                        </Button> */}
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}

