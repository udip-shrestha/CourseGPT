import { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { useApiClient } from "./../ApiClientContext";

export function LoginPage() {
    const navigate = useNavigate();
    const apiClient = useApiClient();
  
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
    
        const { data, errorMessage } = await apiClient.login(email, password);
    
        if (errorMessage) {
            setError(errorMessage);
        }

        const instructorId = data.instructor_id;
        navigate(`/instructors/${instructorId}/profile`);
    
        setIsLoading(false);
    };

    return (
        // Centering container for the card
        <div className="w-full flex items-center justify-center p-4">
            {/* Responsive Card */}
            <Card className="w-full max-w-md shadow-md"> {/* Use max-w-* for responsiveness */}
                {/* Removed the extra <header> and h1#title, assuming title comes from Header component */}
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
                                placeholder="m@example.com" // More helpful placeholder
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                aria-invalid={!!error} // Indicate error state for accessibility
                            />
                        </div>
                        {/* Password Input */}
                        <div className="grid gap-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="********" // Use placeholder for password
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                aria-invalid={!!error} // Indicate error state
                            />
                        </div>

                        {/* Error Message Display */}
                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {/* Sign In Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Signing in..." : "Sign in"}
                        </Button>

                        {/* --- UPDATED REGISTER BUTTON --- */}
                        <Button
                            type="button" // Important: Change type to prevent form submission
                            variant="outline" // Style to differentiate from Sign In
                            className="w-full"
                            onClick={() => navigate('/register')} // Navigate to the register route
                            disabled={isLoading} // Optional: disable if login is in progress
                        >
                            Create New Account
                        </Button>
                        {/* --- END OF UPDATE --- */}

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

